import docker
from django.conf import settings


def get_docker_client():
    return docker.DockerClient(base_url=settings.DOCKER_HOST)