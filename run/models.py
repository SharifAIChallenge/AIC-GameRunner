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

    def compile_for_input(self, parameter_path):
        """
        If the parameter is a string, this method
        stores it in the parameter_path.
        If the parameter is a file, it copies
        the file to the given path.
        """
        if self.parameter.is_input:
            if self.parameter.type == 'string':
                with open(parameter_path, "w") as file:
                    file.write(self.value)
            elif self.parameter.type == 'file':
                shutil.copy(self.value.name, parameter_path)
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
                    parameter_path = os.path.join(shared_path, self.parameter.name)
                    if parameter.is_input:
                        try:
                            value = self.parameter_value_set.get(parameter=parameter)
                            value.compile_for_input(parameter_path)
                        except ParameterValue.DoesNotExist:
                            if parameter.is_required:
                                raise AssertionError("Input parameter {} is required but is not given".format(parameter.name))
                            else:
                                parameter_path = "/dev/null"
                    else:
                        try:
                            self.parameter_value_set.get(parameter=parameter).delete()
                        except ParameterValue.DoesNotExist:
                            pass
                        output_parameters.append(parameter)
                    context[parameter.name] = parameter_path

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
            memlim_sum = 0.0
            cpulim_sum = 0.0
            with open(compiled_compose_file_path) as file:
                compose = yaml.load(file)
                for name in compose['services'] :
                    x = compose['services'][name]['deploy']['resources']['limits']
                    cpulim_sum += float(x['cpus'])
                    s = x['memory']
                    if __name__ == '__main__':
                        if s[-1] == 'K':
                            memlim_sum += int(s[:-1])
                        elif s[-1] == 'M':
                            memlim_sum += int(s[-1]) * 1024
                        elif s[-1] == 'G':
                            memlim_sum += int(s[-1]) * 1024 * 1024
                        else:
                            raise TypeError

                # docker service create ...

                #while [ 1 -ne `docker service ps $name | tail -n +2 | awk '{print $5}' | grep Shutdown | wc -l` ] ; do sleep 0.5; done

        # Section 5: Save outputs. Set run status to success
        for parameter in output_parameters:
            with open(context[parameter.name]) as file:
                file_ = File.objects.create(file=DjangoFile(file))
                parameter_value = ParameterValue(run=self, parameter=parameter)
                parameter_value.value = file_
                parameter_value.save()
        self.status = self.SUCCESS
        self.save()
