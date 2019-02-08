import docker
from django.conf import settings


def get_docker_client():
    client = docker.DockerClient(base_url=settings.DOCKER_HOST)
    client.login(
        username=settings.DOCKER_REGISTRY_USERNAME,
        password=settings.DOCKER_REGISTRY_PASSWORD,
        registry=settings.DOCKER_REGISTRY_URL,
        reauth=False,
    )
    return client
