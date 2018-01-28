import json

from django.db import models
from django.template import Engine, Context
from django.core.files import File as DjangoFile

import requests

from game_runner.utils import get_docker_client
from storage.models import File
from game_runner import settings
from game.models import OperationParameter, Game, Operation
import uuid
import tempfile
import os
import shutil
import subprocess
from django.utils import timezone

import time

from compose.config.config import ConfigFile

import logging

logger = logging.getLogger(__name__)


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
                shutil.copy(self.value.file.path, parameter_path)
                return parameter_path
        raise AssertionError("Unsupported parameter")


class Run(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    operation = models.ForeignKey(Operation)
    request_time = models.DateTimeField(auto_now_add=True, null=True)
    start_time = models.DateTimeField(null=True)
    end_time = models.DateTimeField(null=True)
    queue_reference_id = models.CharField(null=True, max_length=200)
    response_queue_reference_id = models.CharField(null=True, max_length=200)
    owner = models.ForeignKey("api.Token", null=True, blank=True)
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
    WAITING = 0
    SENDING = 1
    SENT = 2
    response_choices = (
        (WAITING, 'Wating'),
        (SENDING, 'Sending'),
        (SENT, 'Sent'),
    )
    status = models.SmallIntegerField(choices=status_choices, default=PENDING)
    response = models.SmallIntegerField(choices=response_choices, default=WAITING)

    def __str__(self):
        return "{}:{}".format(str(self.operation), self.pk)

    def compile_compose_file(self):
        # Section 0: Set run status to running
        logger.info("Starting execution of run {}".format(str(self)))
        self.start_time = timezone.now()
        self.status = self.RUNNING
        self.queue_reference_id = None  # Releasing queue id
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
                        open(template_value, 'a').close()  # Touch the file, making sure it exists
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
                logger.warning(rendered_compose_file)
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
                    memlim_sum += int(service_memory_constraint[:-1]) * 1024 * 1024
                elif service_memory_constraint[-1].upper() == 'G':
                    memlim_sum += int(service_memory_constraint[:-1]) * 1024 * 1024 * 1024
                else:
                    raise TypeError

            cpu_tot_reserve = (MANAGER_CPU_LIMIT
                               if MANAGER_CPU_LIMIT is not None else 0) + cpulim_sum
            mem_tot_reserve = (MANAGER_MEMORY_LIMIT
                               if MANAGER_MEMORY_LIMIT is not None else 0) + memlim_sum

            logger.debug("Total memory limit:{}, Total cpus:{}".format(mem_tot_reserve, cpu_tot_reserve))
            logger.info("Starting execution")
            client = get_docker_client()
            manager_uid = str(self.pk)

            manager_service_spec = ["docker service create", "--name {}".format(manager_uid), ]

            manager_service_spec.append("-e MANAGER_UID={}".format(manager_uid))
            if self.operation.manager_service:
                manager_service_spec.append("-e MANAGER_LISTEN_SERVICE={}".format(
                    self.operation.manager_service
                ))

            cpu_tot_reserve = int(cpu_tot_reserve)
            mem_tot_reserve = int(mem_tot_reserve)

            if MANAGER_CPU_LIMIT:
                manager_service_spec.append("--limit-cpu={}".format(MANAGER_CPU_LIMIT))
            if MANAGER_MEMORY_LIMIT:
                manager_service_spec.append("--limit-memory={}B".format(MANAGER_MEMORY_LIMIT))
            if cpu_tot_reserve > 0:
                manager_service_spec.append("--reserve-cpu={}".format(cpu_tot_reserve))
            if mem_tot_reserve > 0:
                manager_service_spec.append("--reserve-memory={}B".format(mem_tot_reserve))

            manager_service_spec.append('--restart-condition="none"')
            manager_service_spec.append('--mount type=bind,src={},dst=/compose'.format(shared_path))
            manager_service_spec.append('--mount type=bind,src=/var/run/docker.sock,dst=/var/run/docker.sock')

            manager_service_spec.append('kondor-manager') # TODO: Allow custom manager image name using settings

            manager_service_creation_command = ' '.join(manager_service_spec)

            print ("Invoking service with command {}".format(manager_service_creation_command))

            subprocess.call('docker images', shell=True)  # TODO : Use list instead of string
            subprocess.call(manager_service_creation_command, shell=True)  # TODO : Use list instead of string
            subprocess.call('docker images', shell=True)  # TODO : Use list instead of string

            time.sleep(5)
            manager = client.services.list(filters={"name": manager_uid})
            print( "manager len={}".format(len(manager)) );
            if len(manager) == 0:
                raise AssertionError("Service should have been created")
            elif len(manager) != 1:
                print( "len(manager) is greater than 1\n" + str(manager) );
            manager = manager[0]

            # TODO: Use docker interface to wait for the manager
            # TODO: Time limit

            self.log = ""
            failed = False

            logging.info("Waiting for the tasks to be started")
            while len(manager.tasks(filters={'desired-state': 'running'})) == 0 and \
                    len(manager.tasks(filters={'desired-state': 'shutdown'})) == 0:
                logging.info("Checking if job has started")
                time.sleep(STATUS_CHECK_PERIOD)

            logging.info("Waiting for the tasks to be finished")
            start_time = time.time()
            while len(manager.tasks(filters={'desired-state': 'shutdown'})) == 0:
                logging.info("Checking if job is done")
                current_time = time.time()
                if current_time - start_time > self.operation.time_limit:
                    failed = True
                    logging.info("ERROR: Timeout")
                    self.log += "ERROR: Killing manager due to timeout after {} seconds\n".format(
                        current_time - start_time
                    )
                    break
                time.sleep(STATUS_CHECK_PERIOD)

           
            logging.info("Cleaning up")
            manager.remove()

            # TODO: Cleaning spawned services in here should just be a fail-safe.
            # Manager should be reponsible for cleaning up when being killed.

            # FIXME: Stacks aren't currently supported in Docker API
            # The following line assumes services for a stack are named
            # in a specific manner. This must be changed to be implemented
            # using the API.

            
            #services = client.services.list(filters={"name": "{}_".format(manager_uid)})
            #for service in services:
            #    service.remove()
            
            subprocess.call( "docker stack rm {}".format(manager_uid) , shell=True )

            logging.info("Execution finished")
            # Section 5: Save outputs. Set run status to success

            for parameter in output_parameters:
                if not os.path.isfile(context[parameter.name]):
                    self.log += "ERROR: Parameter {} not found.\n"
                    failed = True
            if not failed:
                logging.info("Extracting outputs and saving results")
                for parameter in output_parameters:
                    if not os.path.isfile(context[parameter.name]):
                        self.log += "ERROR: Parameter {} not found.\n"
                        failed = True
                    else:
                        with open(context[parameter.name], 'rb') as file:
                            file_ = File()
                            file_.file.save(parameter.name, DjangoFile(file))
                            file_.owner = self.owner
                            file_.save()
                            parameter_value = ParameterValue(run=self, parameter=parameter)
                            parameter_value.value = file_
                            parameter_value.save()

            self.status = self.FAILURE if failed else self.SUCCESS
            self.end_time = timezone.now()
            self.response = self.SENDING
            self.save()
            logging.info("Done. status: {}".format("failed" if failed else "success"))

    def send_response(self):
        response = [{'id': self.id}, {'operation': self.operation},
                    {'status': self.status}, {'end_time': self.end_time},
                    {'log': self.log}]
        parameters = []
        for parameter_value in self.parameter_value_set.all().filter(parameter__is_input=False):
            parameters.append({parameter_value.parameter.name: parameter_value.value})
        response.append({'parameters': parameters})
        headers = {'Authorization': 'Token{}'.format(self.owner.key)}
        res = requests.post(settings.SITE_URL, data=json.dumps(response), headers=headers)
        logging.log(logging.DEBUG, res.text)

        if res.text == 'OK':
            self.response = self.SENT
        else:
            self.response_queue_reference_id = None
        self.save()
