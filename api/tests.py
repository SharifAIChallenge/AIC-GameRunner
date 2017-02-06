from django.test import TestCase
from rest_framework import exceptions
from rest_framework.parsers import JSONParser
from io import BytesIO

from rest_framework.test import APIClient

from api.models import Token, IPBinding
from game.models import Game, OperationParameter, Operation
from run.models import Run, ParameterValue
from storage.models import File


# Create your tests here.
class TestRunAPI(TestCase):
    def setUp(self):
        self.game_1 = Game(name='AIC 2017')
        self.game_1.save()
        # test won't cover the template functionality
        self.operation_1 = Operation(game=self.game_1, name='run', config='some yml don\'t know what')
        self.operation_1.save()
        self.operation_parameter_1 = OperationParameter(operation=self.operation_1, name='client_1', type='file',
                                                        required=True, is_input=True)
        self.operation_parameter_2 = OperationParameter(operation=self.operation_1, name='log', type='file',
                                                        required=False, is_input=False)
        self.operation_parameter_1.save()
        self.operation_parameter_2.save()
        self.run_1 = Run(start_time='2017-01-15 19:51:06', end_time='2017-01-15T19:51:06Z', operation=self.operation_1)
        self.run_1.save()
        self.file_1 = File()
        self.file_1.save()
        self.param_value_1 = ParameterValue(run=self.run_1, parameter=self.operation_parameter_1, _value=self.file_1.id)
        self.param_value_2 = ParameterValue(run=self.run_1, parameter=self.operation_parameter_2, _value=self.file_1.id)
        self.param_value_1.save()
        self.param_value_2.save()
        # create not restricted token
        self.non_restricted_token = Token(ip_restricted=False, key=Token.generate_key())
        self.non_restricted_token.save()
        # create locally restricted token
        self.local_restricted_token = Token(ip_restricted=True, key=Token.generate_key())
        self.local_restricted_token.save()
        self.local_ip_binding = IPBinding(ip='127.0.0.1', Token=self.local_restricted_token)
        self.local_ip_binding.save()
        # create nonlocally restricted token
        self.nonlocal_restricted_token = Token(ip_restricted=True, key=Token.generate_key())
        self.nonlocal_restricted_token.save()
        self.nonlocal_ip_binding = IPBinding(ip='127.0.0.2', Token=self.nonlocal_restricted_token)
        self.nonlocal_ip_binding.save()

    def safe_authorize(self):
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.non_restricted_token.key)

    def test_report_view(self):
        self.safe_authorize()
        response = self.client.post('/api/run/report', data='{"time": "2017-01-15 19:51:06"}',
                                    content_type='application/json')
        data = JSONParser().parse(BytesIO(response.content))[0]
        self.assertTrue('id' in data)
        self.assertTrue('log' in data)
        self.assertTrue('parameters' in data)
        self.assertFalse('client_1' in data['parameters'])
        self.assertTrue('log' in data['parameters'])
        self.assertEqual(data['end_time'], '2017-01-15T19:51:06Z')
        self.assertEqual(data['status'], 3)

    def test_create_view_bad_request(self):
        self.safe_authorize()
        response = self.client.post('/api/run/run',
                                    data='[{"parameter_value_set":{}}]',
                                    content_type='application/json')
        data = JSONParser().parse(BytesIO(response.content))
        self.assertFalse(data[0]['success'])

    def test_create_view(self):
        self.safe_authorize()
        response = self.client.post('/api/run/run',
                                    data='[{"operation":"run","parameters":{"client_1":"%s"}}]' % self.file_1.id,
                                    content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = JSONParser().parse(BytesIO(response.content))
        self.assertTrue(data[0]['success'])

    def test_non_restricted_token_authorization(self):
        self.safe_authorize()
        response = self.client.post('/api/run/report', data='{"time": "2017-01-15 19:51:06"}',
                                    content_type='application/json')
        self.assertEqual(response.status_code, 200)

    def test_invalid_token_authorization(self):
        response = self.client.post('/api/run/report', data='{"time": "2017-01-15 19:51:06"}',
                                    content_type='application/json', HTTP_AUTHORIZATION='Token ' + 'fakeToken')
        self.assertRaises(exceptions.AuthenticationFailed)

    # checks that locally restricted token works when the client is local
    def test_locally_restricted_token_authorization(self):
        response = self.client.post('/api/run/report', data='{"time": "2017-01-15 19:51:06"}',
                                    content_type='application/json',
                                    HTTP_AUTHORIZATION='Token ' + self.local_restricted_token.key)
        self.assertEqual(response.status_code, 200)

    # checks that non locally restricted token does not works when the client is local
    def test_non_locally_restricted_token_authorization(self):
        response = self.client.post('/api/run/report', data='{"time": "2017-01-15 19:51:06"}',
                                    content_type='application/json',
                                    HTTP_AUTHORIZATION='Token ' + self.nonlocal_restricted_token.key)
        self.assertRaises(exceptions.AuthenticationFailed)
