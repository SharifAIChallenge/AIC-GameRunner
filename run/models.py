import json

from django.db import models

import requests

from storage.models import File
from game_runner import settings
from game.models import OperationParameter, Game, Operation
import uuid
from django.utils import timezone


import logging

logger = logging.getLogger(__name__)


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


class Run(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    operation = models.ForeignKey(Operation)
    request_time = models.DateTimeField(auto_now_add=True, null=True)
    start_time = models.DateTimeField(null=True)
    end_time = models.DateTimeField(null=True)
    queue_reference_id = models.CharField(null=True, max_length=200)
    response_queue_reference_id = models.CharField(null=True, max_length=200)
    owner = models.ForeignKey("api.Token", null=True, blank=True)
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
    WAITING = 0
    SENDING = 1
    SENT = 2
    response_choices = (
        (WAITING, 'Waiting'),
        (SENDING, 'Sending'),
        (SENT, 'Sent'),
    )
    status = models.SmallIntegerField(
        choices=status_choices,
        default=PENDING,
    )
    response = models.SmallIntegerField(
        choices=response_choices,
        default=WAITING,
    )
    count_tries = models.SmallIntegerField(default=0)

    def __str__(self):
        return "{}:{}".format(str(self.operation), self.pk)

    def send_response(self):
        from api.serializers import RunReportSerializer

        headers = {'Authorization': '{}'.format(self.owner.key)}
        serializer = RunReportSerializer(self)
        serializer.data['id'] = str(serializer.data['id'])
        data = serializer.data
        try:
            data = json.dumps(data)
            logger.info("TESTIG JSON " + str(data))
            res = requests.post(settings.SITE_URL, data=data, headers=headers)
            logger.info(res.status_code)
            if res.status_code == 200:
                self.response = self.SENT
            else:
                self.count_tries += 1
        except Exception as e:
            logger.exception(e)
        if self.count_tries >= settings.RETRY_LIMIT:
            self.queue_reference_id = None
            self.status = self.PENDING
            self.response = self.WAITING
            self.count_tries = 0
        self.response_queue_reference_id = None
        self.save()

    def start_execute(self):
        self.start_time = timezone.now()
        self.status = self.RUNNING
        self.queue_reference_id = None  # Releasing queue id
        self.save()

    def execute_done(self):
        self.status = self.SUCCESS
        self.save()
        self.end_execute()

    def execute_failed(self):
        self.status = self.FAILURE
        self.save()
        self.end_execute()

    def end_execute(self):
        self.end_time = timezone.now()
        self.save()

    def start_sending_response(self):
        self.response = self.SENDING
        self.response_queue_reference_id = None
        self.save()
