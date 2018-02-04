import logging
from django.core.management.base import BaseCommand, CommandError
from run.models import Run

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Rerun failed runs'

    def response(self, message):
        logger.info(message)
        self.stdout.write(message)

    def handle(self, *args, **options):
        failedruns = Run.objects.filter(status = Run.FAILURE)
        for failedrun in failedruns:

            failedrun.status = Run.PENDING
            failedrun.queue_refrence_id = None

            failedrun.response = Run.WAITING
            failedrun.response_queue_refrence_id = None

            for parameter_value in failedrun.parameter_value_set.all():
                parameter_value.delete()

            failedrun.save()

            self.response(failedrun.__str__())

        if len(failedruns) == 0:
            self.response("No failed run found.")
        else:
            self.response("All failed runs changed to pending ...")
