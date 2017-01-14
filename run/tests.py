import time
from django.test import TestCase
from .models import Run
from . import views


# Create your tests here.
class TestRunAPI(TestCase):
    def setUp(self):
        self.run_1 = Run(start_time=time.time())
        self.run_1.save()

    def test_report_view(self):
        response = self.client.post(views.report, '{"from_time":"0-0-0"}')
        print(response)
