import uuid
from django.db import models
from django.conf import settings

from api.models import Token


class File(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(Token, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    file = models.FileField(upload_to='uploads')
