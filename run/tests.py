from django.test import TestCase
from model_mommy import mommy

from .models import Run


class RunTestModel(TestCase):
    def setUp(self):
        self.test_instance = mommy.make(Run, queue_reference_id=None)

    def test_queue_id_for_run(self):
        self.assertIsNotNone(self.test_instance.queue_reference_id)
