from django.db import models
from storage.models import File
from game_runner import settings
import uuid


# Initial scheme
# FilePath
#   +file : File
#   +path : String
#   +run : Run
#
# Run
#   +token : Token
#   +request_time : DateTime
#   +start_time : DateTime
#   +end_time : DateTime
#   +input_file_paths : FilePath[]
#   +output_file_paths : FilePath[]
#   +log : File
#   +game : Game
#
# API Methods:
#   +run((game : Game, file_paths : FilePath[])[]) : tokens String[]
#   +report(from_time : DateTime) : runs : Run[]

class ParameterValue(models.Model):
    _value = models.TextField()
    run = models.ForeignKey('Run', related_name='parameter_value_set')
    # parameter = models.ForeignKey('Parameter') later should be uncommented

    @property
    def value(self):
        # if parameter.type == 'String':
        #     return self._value
        # else:
        #     return File.objects.get(id=self._value)
        return None


class Run(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    request_time = models.DateTimeField(auto_now_add=True, null=True)
    start_time = models.DateTimeField(null=True)
    end_time = models.DateTimeField(null=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True)
    log = models.TextField()
    # choices for the status
    PENDING = 3
    SUCCESS = 1
    FAILURE = 2
    status_choices = (
        (SUCCESS, 'Success'),
        (FAILURE, 'Failure'),
        (PENDING, 'Pending'),
    )
    status = models.SmallIntegerField(choices=status_choices, default=PENDING)
    # game = Game()