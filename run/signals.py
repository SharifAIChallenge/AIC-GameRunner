from django.db.models.signals import post_save
from django.dispatch import receiver

from run.models import Run
from run.tasks import schedule_run_execution


@receiver(post_save, sender=Run)
def run_handler(instance, **kwargs):
    schedule_run_execution(instance)