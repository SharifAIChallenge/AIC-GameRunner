import shutil
import tempfile

import docker
from django.db import models

from game_runner import settings


class DockerFile(models.Model):
    name = models.CharField(max_length=50, primary_key=True)
    file = models.FileField(upload_to='dockerfiles')
    version = models.IntegerField(editable=False)
    memorylimit = models.IntegerField(help_text='maximum memory usage allowed in KBs', blank=True,
                                      null=True)  # TODO: Check KBs
    cpushare = models.IntegerField(help_text='CPU shares (relative weight)', blank=True, null=True)
    latest_image_version = models.IntegerField(editable=False, default=0)

    def save(self):
        if getattr(self, 'version') is None:
            self.version = 0
        self.version += 1
        super(DockerFile, self).save()
        # self.build_and_push()

    # TODO: update latest_image_version if push was successful
    def build_and_push(self):
        tmpfolder = tempfile.TemporaryDirectory()
        shutil.copyfile(settings.MEDIA_ROOT + self.file.name, tmpfolder.name + '/Dockerfile')
        for resource in list(self.resource_set.all()):
            shutil.copy(settings.MEDIA_ROOT + resource.file.name, tmpfolder.name)
        client = docker.DockerClient(base_url='unix://var/run/docker.sock')
        images = client.images
        images.build(path=tmpfolder.name,
                     tag=settings.DOCKER_REGISTRY_URL + '/' + self.name + ':' + self.version.__str__(),
                     container_limits=self.get_limits())
        images.build(path=tmpfolder.name, tag=settings.DOCKER_REGISTRY_URL + '/' + self.name,
                     container_limits=self.get_limits())
        images.push(settings.DOCKER_REGISTRY_URL + '/' + self.name, tag=self.version.__str__(), insecure_registry=True)
        images = images.push(settings.DOCKER_REGISTRY_URL + '/' + self.name, tag='latest', insecure_registry=True)
        pass

    def __str__(self):
        return 'Dockerfile= ' + self.name + ':' + self.version.__str__() + \
               ' / Latest image version= ' + self.latest_image_version.__str__()

    def get_limits(self):
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
