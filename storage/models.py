import uuid
from os.path import basename
from tempfile import TemporaryFile
from urllib.parse import urlsplit

import requests
from django.db import models

from api.models import Token
from django.core.files import File as DjangoFile


class File(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(Token, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    file = models.FileField(upload_to='uploads')

    def retrieve_from_url(self, url):
        with TemporaryFile() as tf:
            r = requests.get(url, stream=True)
            if r.status_code != 200:
                raise self.FileNotFoundError("File url is invalid. {}".format(r.status_code))
            for chunk in r.iter_content(chunk_size=4096):
                tf.write(chunk)
            tf.seek(0)
            self.file.save(basename(urlsplit(url).path), DjangoFile(tf))

    def __str__(self):
        return '{}:{}'.format(self.id, self.owner)

    class FileNotFoundError(Exception):
        pass
