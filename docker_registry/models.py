import shutil
import tempfile

import docker
import os
from django.db import models
from docker.errors import BuildError

from game_runner import settings


class DockerFile(models.Model):
    name = models.CharField(max_length=50, primary_key=True)
    file = models.FileField(upload_to='dockerfiles')
    version = models.IntegerField(editable=False)
    memorylimit = models.IntegerField(help_text='maximum memory usage allowed in KBs', blank=True,
                                      null=True)  # TODO: Check KBs
    cpushare = models.IntegerField(help_text='CPU shares (relative weight)', blank=True, null=True)
    latest_image_version = models.IntegerField(editable=False, default=0)
    latest_build_and_push_log = models.TextField(editable=False, blank=True, null=False, default='')

    def save(self, *args, **kwargs):
        if getattr(self, 'version', None) is None:
            self.version = 0
        self.version += 1
        super(DockerFile, self).save(*args, **kwargs)

    def build_and_push(self):
        with tempfile.TemporaryDirectory() as tmpfolder:
            for resource in self.resource_set.all():
                # TODO : Make sure the following line is not a security risk.
                resource_dir = os.path.dirname(os.path.abspath(resource.name))
                os.makedirs(os.path.join(tmpfolder, resource_dir), exist_ok=True)
                shutil.copy(resource.file.path, os.path.join(tmpfolder, resource.name))
            shutil.copyfile(self.file.path, os.path.join(tmpfolder, 'Dockerfile'))
            client = docker.DockerClient(base_url=settings.DOCKER_HOST)
            images = client.images
            image_repository_name = settings.DOCKER_REGISTRY_URL + '/' + self.name
            image_tag = str(self.version)
            self.latest_build_and_push_log = ''
            try:
                current_image = images.build(path=tmpfolder,
                                             tag=image_repository_name,
                                             container_limits=self._get_limits())
                self.latest_build_and_push_log = 'Image successfully built.'
            except BuildError as e:
                self.latest_build_and_push_log = 'Build failed. \n' + str(e)
                current_image = None
            if current_image is not None:
                current_image.tag(repository=image_repository_name, tag=image_tag)
                versioned_push_log = images.push(image_repository_name, tag=image_tag)
                self.latest_build_and_push_log += '\n' + versioned_push_log
                latest_push_log = images.push(image_repository_name, tag='latest')
                self.latest_build_and_push_log += '\n' + latest_push_log
                # TODO: update latest_image_version if push was successful

            self.save()

    def __str__(self):
        return 'Dockerfile= ' + self.name + ':' + self.version.__str__() + \
               ' / Latest image version= ' + self.latest_image_version.__str__()

    def _get_limits(self):
        limits = {}
        if self.memorylimit is not None:
            limits['memory'] = self.memorylimit
        if self.cpushare is not None:
            limits['cpushares'] = self.cpushare
        return limits


# @receiver(post_save, sender=DockerFile)
# def build_and_push(sender, instance, **kwargs):
#     instance.build_and_push()

class Resource(models.Model):
    name = models.CharField(max_length=50, primary_key=True)
    file = models.FileField(upload_to='sourcefiles')
    dockerfile = models.ForeignKey(DockerFile, on_delete=models.CASCADE)
