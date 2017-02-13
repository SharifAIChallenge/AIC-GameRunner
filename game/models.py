# -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.conf import settings


__all__ = ["Game", "Operation", "OperationResource", "OperationParameter"]


class Game(models.Model):
    name = models.CharField(verbose_name=_('name'), max_length=100)

    def __str__(self):
        return self.name


class Operation(models.Model):
    game = models.ForeignKey(to=Game, verbose_name=_('game'), null=False, blank=False)
    name = models.CharField(verbose_name=_('name'), max_length=100)
    config = models.TextField(verbose_name=_("docker compose yml template"), null=False)
    time_limit = models.IntegerField(verbose_name=_("Time limit"),
                                     help_text=_("in seconds. "
                                                 "WARNING: this time limit is not strict. "
                                                 "i.e. it's possible that the system allows an operation to "
                                                 "continue running for slightly less or more time than "
                                                 "specified here."),
                                     default=120,
                                     )

    class Meta:
        unique_together = (("game", "name"), )

    def __str__(self):
        return "{}:{}".format(str(self.game), self.name)


class OperationResource(models.Model):
    operation = models.ForeignKey(Operation, verbose_name=_("operation"), related_name="resources")
    name = models.CharField(max_length=100, verbose_name=_("name"))
    file = models.FileField(verbose_name=_("file"))

    class Meta:
        unique_together = (("operation", "name"), )

    def __str__(self):
        return "{}:{}".format(str(self.operation), self.name)


class OperationParameter(models.Model):
    PARAMETER_TYPES = (
        ('string', 'string'),
        ('file', 'file'),
    )

    operation = models.ForeignKey(Operation, verbose_name=_("operation"), related_name="parameters")
    name = models.CharField(max_length=100, verbose_name=_("name"))
    type = models.CharField(choices=PARAMETER_TYPES, verbose_name=_("type"), max_length=20)
    required = models.BooleanField(verbose_name=_("required"), default=True)
    is_input = models.BooleanField(verbose_name=_("is input?"))
    max_size = models.IntegerField(verbose_name=_("max size in bytes"), default=0, help_text="Use 0 for unlimited")

    class Meta:
        unique_together = (("operation", "name"), )

    def __str__(self):
        return "{}:{}".format(str(self.game), self.name)
