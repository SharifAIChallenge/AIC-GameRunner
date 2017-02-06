from __future__ import absolute_import, unicode_literals
from celery import shared_task


@shared_task
def run(instance_pk):
    from .models import Run
    instance = Run.objects.get(pk=instance_pk)
    instance.run()
