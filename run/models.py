from django.db import models
from django.template import Engine, Context
from django.core.files import File as DjangoFile

from storage.models import File
from game_runner import settings
from game.models import OperationParameter, Game, Operation
import uuid
import tempfile
import os
import shutil
import yaml

import docker
from docker.types import Resources as DockerResources
from docker.types import RestartPolicy as DockerRestartPolicy

import time

from compose.config.config import ConfigFile


class ParameterValue(models.Model):
    _value = models.TextField()
    run = models.ForeignKey('Run', related_name='parameter_value_set')
    parameter = models.ForeignKey(OperationParameter)

    @property
    def value(self):
        if self.parameter.type == 'string':
            return self._value
        else:
            return File.objects.get(pk=self._value)

    @value.setter
    def value(self, value):
        if self.parameter.type == 'string':
            if not isinstance(value, str):
                raise ValueError()
            self._value = value
        else:
            if not isinstance(value, File):
                raise ValueError()
            self._value = value.pk

    def compile_for_input(self, dir):
        """
        If the parameter is a string, this method
        returns the value
        If the parameter is a file, it copies it to
        a file inside `dir` and returns the path.
        """
        if self.parameter.is_input:
            if self.parameter.type == 'string':
                return self.value
            elif self.parameter.type == 'file':
                parameter_path = os.path.join(dir, self.parameter.name)
                shutil.copy(self.value.name, parameter_path)
                return parameter_path
        raise AssertionError("Unsupported parameter")


class Run(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    operation = models.ForeignKey(Operation)
    request_time = models.DateTimeField(auto_now_add=True, null=True)
    start_time = models.DateTimeField(null=True)
    end_time = models.DateTimeField(null=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True)
    log = models.TextField()
    # choices for the status
    PENDING = 0
    RUNNING = 1
    SUCCESS = 2
    FAILURE = 3
    status_choices = (
        (PENDING, 'Pending'),
        (SUCCESS, 'Success'),
        (RUNNING, 'Running'),
        (FAILURE, 'Failure'),
    )
    status = models.SmallIntegerField(choices=status_choices, default=PENDING)

    def compile_compose_file(self):
        # Section 0: Set run status to running
        self.status = self.RUNNING
        self.save()

        COMPOSE_FILE_NAME = "docker-compose.yml"
        MANAGER_CPU_LIMIT = None
        MANAGER_MEMORY_LIMIT = None
        STATUS_CHECK_PERIOD = 10

        with tempfile.TemporaryDirectory(prefix=settings.NFS_DIR) as shared_path:

            with tempfile.TemporaryDirectory() as tmp_path:

                # Section 1: Gather all resources and config file into a single folder
                template_compile_path = os.path.join(tmp_path, "compile")
                os.makedirs(template_compile_path)
                raw_compose_file_path = os.path.join(template_compile_path, COMPOSE_FILE_NAME)
                with open(raw_compose_file_path, "w") as file:
                    file.write(self.operation.config)
                for resource in self.operation.resources.all():
                    shutil.copyfile(
                        resource.file.name,
                        os.path.join(template_compile_path, resource.name)
                    )

                # Section 2: Compile a dictionary with all parameters
                context = {}
                output_parameters = []
                for parameter in self.operation.parameters.all():
                    if parameter.is_input:
                        try:
                            value = self.parameter_value_set.get(parameter=parameter)
                            template_value = value.compile_for_input(shared_path)
                        except ParameterValue.DoesNotExist:
                            if parameter.is_required:
                                raise AssertionError("Input parameter {} is required but is not given".format(parameter.name))
                            else:
                                template_value = parameter.get_non_existant_value()
                    else:
                        try:
                            self.parameter_value_set.get(parameter=parameter).delete()
                        except ParameterValue.DoesNotExist:
                            pass
                        output_parameters.append(parameter)
                        template_value = os.path.join(shared_path, parameter.name)
                    context[parameter.name] = template_value

                # TODO: Resources are used for different purposes. Separate them.

                for resource in self.operation.resources.all():
                    resource_path = os.path.join(shared_path, resource.name)
                    shutil.copyfile(
                        resource.file.name,
                        resource_path
                    )
                    context[resource.name] = resource_path

                # Section 3: Compile config file
                template_engine = Engine(
                    dirs=[template_compile_path],
                    loaders=['django.template.loaders.filesystem.Loader'],
                )
                template = template_engine.get_template(COMPOSE_FILE_NAME)
                rendered_compose_file = template.render(Context(context))

                compiled_compose_file_path = os.path.join(shared_path, COMPOSE_FILE_NAME)
                with open(compiled_compose_file_path, "w") as file:
                    file.write(rendered_compose_file)

            # Section 4: Provide config file to the manager node and run it

            # TODO: Use docker-compose interface to calculate sum of limits

            memlim_sum = 0.0
            cpulim_sum = 0.0
            compose = ConfigFile.from_filename(compiled_compose_file_path)
            for service_name in compose.get_service_dicts():
                service = compose.get_service(service_name)
                try:
                    limits = service['deploy']['resources']['limits']
                except KeyError:
                    continue
                cpulim_sum += float(limits.get('cpus', 0))
                service_memory_constraint = limits.get('memory', "0B")
                if service_memory_constraint[-1].upper() == 'B':
                    memlim_sum += int(service_memory_constraint[:-1])
                if service_memory_constraint[-1].upper() == 'K':
                    memlim_sum += int(service_memory_constraint[:-1]) * 1024
                elif service_memory_constraint[-1].upper() == 'M':
                    memlim_sum += int(service_memory_constraint[-1]) * 1024 * 1024
                elif service_memory_constraint[-1].upper() == 'G':
                    memlim_sum += int(service_memory_constraint[-1]) * 1024 * 1024 * 1024
                else:
                    raise TypeError

                client = docker.from_env()
                manager = client.services.create(
                    image='kondor-manager',
                    resources=DockerResources(
                        cpu_limit=(MANAGER_CPU_LIMIT * (10 ** 9))
                        if MANAGER_CPU_LIMIT is not None else None,
                        mem_limit=MANAGER_MEMORY_LIMIT,
                        cpu_reservation=(
                                            (MANAGER_CPU_LIMIT
                                             if MANAGER_CPU_LIMIT is not None else 0) +
                                            cpulim_sum
                                        ) * (10 ** 9),
                        mem_reservation=(
                            (MANAGER_MEMORY_LIMIT
                             if MANAGER_MEMORY_LIMIT is not None else 0) +
                            memlim_sum
                        ),
                    ),
                    restart_policy=DockerRestartPolicy(
                        condition='none'
                    ),
                    mounts=[
                        "{}:/compose:ro".format(shared_path)
                    ]
                )

                # TODO: Use docker interface to wait for the manager
                while len(manager.tasks(filter={'desired-state': 'shutdown'})) == 0:
                    time.sleep(STATUS_CHECK_PERIOD)

        # Section 5: Save outputs. Set run status to success
        for parameter in output_parameters:
            with open(context[parameter.name]) as file:
                file_ = File.objects.create(file=DjangoFile(file))
                parameter_value = ParameterValue(run=self, parameter=parameter)
                parameter_value.value = file_
                parameter_value.save()
        self.status = self.SUCCESS
        self.save()
