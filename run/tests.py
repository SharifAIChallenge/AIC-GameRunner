from django.test import TestCase
from rest_framework.parsers import JSONParser
from io import BytesIO

from .models import Run


# Create your tests here.
class TestRunAPI(TestCase):
    def setUp(self):
        self.run_1 = Run(start_time='2017-01-15 19:51:06', end_time='2017-01-15T19:51:06Z')
        self.run_1.save()

    def test_report_view(self):
        response = self.client.post('/api/run/report', data='{"from_time": "2017-01-15 19:51:06"}',
                                    content_type='application/json')
        data = JSONParser().parse(BytesIO(response.content))[0]
        self.assertTrue('id' in data)
        self.assertTrue('log' in data)
        self.assertTrue('output_file_paths' in data)
        self.assertEqual(data['end_time'], '2017-01-15T19:51:06Z')
        self.assertEqual(data['status'], 3)


