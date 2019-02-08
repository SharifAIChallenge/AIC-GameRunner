import logging
import math
import os
import shutil
import subprocess
import tempfile
import time

from compose.config.config import ConfigFile
from django.conf import settings
from django.template import engines, Context
from django.core.files import File as DjangoFile

from game_runner.utils import get_docker_client
from run.models import Run, ParameterValue
from storage.models import File

logger = logging.getLogger(__name__)

MANAGER_CPU_LIMIT = None
MANAGER_MEMORY_LIMIT = None
STATUS_CHECK_PERIOD = 10


def execute_run(run_id):
    run = Run.objects.get(run_id)
    logger.warning("Starting execution of run {}".format(str(run)))

    # Section 0: Set run status to running
    run.start_execute()

    # Build a temporary folder in nfs
    with tempfile.TemporaryDirectory(prefix=settings.NFS_DIR) as shared_path:

        # Build context dictionary with all parameters
        resources = push_resources(run, shared_path)
        input_params = push_input_parameters(run, shared_path)
        output_params = touch_output_parameters(run, shared_path)

        context = {}
        context.update(resources)
        context.update(input_params)
        context.update(output_params)

        # Render operation config
        template = engines['django'].from_string(run.operation.config)
        rendered_compose_file = template.render(Context(context))

        # save rendered compose file
        compose_file_path = os.path.join(shared_path, "docker-compose.yml")
        with open(compose_file_path, "w") as compose_file:
            compose_file.write(rendered_compose_file)

        # Section 4: Provide config file to the manager node and run it
        # TODO: Use docker-compose interface to calculate sum of limits

        memory_limit, cpu_limit = calculate_resource_limits(compose_file_path)
        logger.debug("Total memory limit:{}, Total cpus:{}".format(
            memory_limit,
            cpu_limit,
        ))
        logger.info("Starting execution")
        client = get_docker_client()
        manager_uid = str(run.pk)


        manager_service_spec = ["docker service create",
                                "--name {}".format(manager_uid),
                                "-e MANAGER_UID={}".format(manager_uid)]
        if run.operation.manager_service:
            manager_service_spec.append("-e MANAGER_LISTEN_SERVICE={}".format(
                run.operation.manager_service
            ))

        cpu_limit = math.ceil(cpu_limit)
        memory_limit = int(memory_limit)

        if MANAGER_CPU_LIMIT:
            manager_service_spec.append("--limit-cpu={}".format(
                MANAGER_CPU_LIMIT
            ))
        if MANAGER_MEMORY_LIMIT:
            manager_service_spec.append("--limit-memory={}B".format(
                MANAGER_MEMORY_LIMIT
            ))
        if cpu_limit > 0:
            manager_service_spec.append("--reserve-cpu={}".format(cpu_limit))
        if memory_limit > 0:
            manager_service_spec.append("--reserve-memory={}B".format(
                memory_limit
            ))

        manager_service_spec += [
            '--restart-condition="none"',
            '--mount type=bind,src={},dst=/compose'.format(shared_path),
            '--mount type=bind,src=/var/run/docker.sock,dst=/var/run/docker.sock',
            '--detach=true',
            'kondor-manager',
        ]
        # TODO: Allow custom manager image name using settings

        manager_service_creation_command = ' '.join(manager_service_spec)
        logger.info("Invoking service with command {}".format(manager_service_creation_command))
        subprocess.call(manager_service_creation_command, shell=True)
        # TODO : Use list instead of string

        time.sleep(5)
        manager = client.services.list(filters={"name": manager_uid})
        if len(manager) == 0:
            raise AssertionError("Service should have been created")
        manager = manager[0]

        # TODO: Use docker interface to wait for the manager
        # TODO: Time limit

        failed = False

        # TODO: remove legacy whiles

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
            if current_time - start_time > run.operation.time_limit:
                failed = True
                logging.info("ERROR: Timeout")
                run.log += "ERROR: Killing manager due to timeout after {} seconds\n".format(
                    current_time - start_time
                )
                break
            time.sleep(STATUS_CHECK_PERIOD)

        # Logging
        # logger.info("Save log files")
        # services = client.services.list(filters={"name": manager_uid})
        # buffer = ""
        # logger.info(len(services))
        # for service in services:
        #     logger.info("Service {} {} saving ...".format(service.name, service.id))
        #     result = subprocess.run("docker service logs {}".format(service.id).split(),
        #                               stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        #     out = result.stdout
        #     buffer = "{}Service {}-{}-{}\n\n{}\n\n\n".format(buffer, service.name, service.id, service.short_id,
        #                                              out.decode("utf-8"))
        # run.service_log.save('{}.log'.format(run.pk), DjangoContentFile(buffer))
        #
        # logging.info("Cleaning up")
        # try:
        #     manager.remove()
        # except Exception as e:
        #     logger.exception(e)

        # TODO: Cleaning spawned services in here should just be a fail-safe.
        # Manager should be reponsible for cleaning up when being killed.

        # FIXME: Stacks aren't currently supported in Docker API
        # The following line assumes services for a stack are named
        # in a specific manner. This must be changed to be implemented
        # using the API.

        #services = client.services.list(filters={"name": "{}_".format(manager_uid)})
        #for service in services:
        #    service.remove()

        subprocess.call("docker stack rm {}".format(manager_uid), shell=True)

        logging.info("Execution finished")
        # Section 5: Save outputs. Set run status to success

        valid = validate_output_parameters(run, output_params)
        if valid:
            logging.info("Extracting outputs and saving results")
            pull_output_parameters(run, output_params)

        if valid:
            run.execute_done()
        else:
            run.execute_failed()

        run.start_sending_response()
        run.send_response()

        logging.info("Done. status: {}".format(
            "failed" if not valid else "success"
        ))


def push_resources(run, path):
    """
    :param run: run model
    :param path: path to save resources files
    :return: dictionary with key value resource : resource_dir
    """
    result = {}
    for resource in run.operation.resources.all():
        resource_path = os.path.join(path, resource.name)
        shutil.copyfile(
            resource.file.name,
            resource_path
        )
        result[resource.name] = resource_path
    return result


def push_input_parameters(run, path):
    """
    :param run: run model
    :param path: path to save input file parameters
    :return: dictionary with key value parameter : parameter_value
    """
    context = {}
    for parameter in run.operation.parameters.filter(is_input=True):
        context[parameter.name] = \
            render_input_parameter_value(run, parameter, path)
    return context


def touch_output_parameters(run, path):
    """
    :param run: run model
    :param path: path to save output file parameters
    :return: dictionary with key value parameter : parameter_value
    """
    context = {}
    for parameter in run.operation.parameters.filter(is_input=False):
        context[parameter.name] = \
            render_output_parameter_value(run, parameter, path)
    return context


def validate_output_parameters(run, output_params):
    """
    :param run: run model
    :param output_params: output parameters dict
    :return: validation boolean
    """
    output_parameters = run.operation.parameters.filter(is_input=False)
    for parameter in output_parameters:
        if not os.path.isfile(output_params[parameter.name]):
            return False
    return True


def pull_output_parameters(run, output_params):
    """
    :param run: run model
    :param output_params: output parameters dict
    :return: None
    """
    output_parameters = run.operation.parameters.filter(is_input=False)
    for parameter in output_parameters:
        with open(output_params[parameter.name], 'rb') as file:
            file_ = File()
            file_.file.save(parameter.name, DjangoFile(file))
            file_.owner = run.owner
            file_.save()
            parameter_value = ParameterValue(run=run, parameter=parameter)
            parameter_value.value = file_
            parameter_value.save()


def render_input_parameter_value(run, parameter, path):
    try:
        parameter_value = run.parameter_value_set.get(parameter=parameter)
    except ParameterValue.DoesNotExist:
        if parameter.is_required:
            raise AssertionError(
                "Input parameter {} is required but is not given.".format(
                    parameter.name
                )
            )
        else:
            return parameter.get_non_existant_value()

    if parameter.type == 'string':
        return parameter_value.value
    if parameter.type == 'file':
        parameter_path = os.path.join(path, parameter.name)
        shutil.copy(parameter_value.value.file.path, parameter_path)
        return parameter_path
    raise AssertionError("Unsupported input parameter {}".format(parameter))


def render_output_parameter_value(run, parameter, path):
    if parameter.type == 'file':
        run.parameter_value_set.filter(parameter=parameter).delete()
        parameter_path = os.path.join(path, parameter.name)
        touch_file_path(parameter_path)
        return parameter_path
    raise AssertionError("Unsupported output parameter {}".format(parameter))


def remove_output_parameter(run):
    run.parameter_value_set.filter(parameter__is_input=False).delete()


def touch_file_path(file_path):
    open(file_path, 'a').close()  # Touch the file, making sure it exists


def calculate_resource_limits(compose_file_path):
    memlim_sum = 0.0
    cpulim_sum = 0.0
    compose = ConfigFile.from_filename(compose_file_path)
    for service_name in compose.get_service_dicts():
        service = compose.get_service(service_name)
        try:
            limits = service['deploy']['resources']['limits']
        except KeyError:
            continue
        cpulim_sum += float(limits.get('cpus', 0))
        memlim_sum += memory_limit_to_int(limits.get('memory', "0B"))

    cpu_tot_reserve = (MANAGER_CPU_LIMIT
                       if MANAGER_CPU_LIMIT is not None else 0) + cpulim_sum
    mem_tot_reserve = (MANAGER_MEMORY_LIMIT
                       if MANAGER_MEMORY_LIMIT is not None else 0) + memlim_sum
    return mem_tot_reserve, cpu_tot_reserve


def memory_limit_to_int(memory_limit):
    units = {'B': 1, 'K': 1024, 'M': 1024*1024, 'G':1024*2014*1024}
    try:
        limit = int(memory_limit[:-1])
        unit_cof = units[memory_limit[-1]]
    except (KeyError, ValueError):
        raise TypeError("Not a memory limit string. (e.g 128K)")
    return limit * unit_cof
