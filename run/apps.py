from django.apps import AppConfig


class RunConfig(AppConfig):
    name = 'run'

    def ready(self):
        from . import signals
