from __future__ import absolute_import, unicode_literals
from celery import shared_task
from .models import Run


def schedule_sending_response(run):
    if run.response_queue_reference_id is None and run.response == Run.SENDING:
        run.response_queue_reference_id = sending_response.delay(run.pk)
        run.save()


def schedule_run_execution(run):
    if run.queue_reference_id is None and run.status == Run.PENDING:
        run.queue_reference_id = execute_run.delay(run.pk)
        run.save()


@shared_task
def execute_run(instance_pk):
    instance = Run.objects.get(pk=instance_pk)
    instance.compile_compose_file()


@shared_task
def sending_response(instance_pk):
    instance = Run.objects.get(pk=instance_pk)
    instance.send_response()


@shared_task
def periodic_check_for_missed_runs():
    for missed_run in Run.objects.filter(queue_reference_id__isnull=True, status=Run.PENDING):
        schedule_run_execution(missed_run)


@shared_task
def periodic_check_for_sending_responses():
    for run in Run.objects.filter(response_queue_reference_id__isnull=True, response=Run.SENDING):
        schedule_sending_response(run)
