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

class FilePath(models.Model):
    file = models.ForeignKey(File, default=None)
    # definition = models.ForeignKey('FileDefinition') later should be uncommented
    run = models.ForeignKey('Run')


class Run(models.Model):
    # token = Token()
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    request_time = models.DateTimeField(auto_now_add=True, null=True)
    start_time = models.DateTimeField(null=True)
    end_time = models.DateTimeField(null=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True)
    input_file_paths = models.ManyToManyField(to=FilePath, related_name='destination_run')
    output_file_paths = models.ManyToManyField(to=FilePath, related_name='source_run')
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
