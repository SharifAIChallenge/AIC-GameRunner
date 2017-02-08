# -*- coding: utf-8 -*-

from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _

__all__ = ["Game", "Operation", "OperationResource", "OperationParameter"]


class Game(models.Model):
    name = models.CharField(verbose_name=_('name'), max_length=100)


class Operation(models.Model):
    game = models.ForeignKey(to=Game, verbose_name=_('game'), null=False, blank=False)
    name = models.CharField(verbose_name=_('name'), max_length=100)
    config = models.TextField(verbose_name=_("docker compose yml template"), null=False)

    class Meta:
        unique_together = (("game", "name"),)

    def __unicode__(self):
        return self.name


class OperationResource(models.Model):
    operation = models.ForeignKey(Operation, verbose_name=_("operation"))
    name = models.CharField(max_length=100, verbose_name=_("name"))
    file = models.FileField(verbose_name=_("file"), upload_to=settings.NFS_DIR)

    class Meta:
        unique_together = (("operation", "name"),)


class OperationParameter(models.Model):
    PARAMETER_TYPES = (
        ('string', 'string'),
        ('file', 'file'),
    )

    operation = models.ForeignKey(Operation, verbose_name=_("operation"))
    name = models.CharField(max_length=100, verbose_name=_("name"))
    type = models.CharField(choices=PARAMETER_TYPES, verbose_name=_("type"), max_length=20)
    required = models.BooleanField(verbose_name=_("required"), default=True)
    is_input = models.BooleanField(verbose_name=_("is input?"))

    class Meta:
        unique_together = (("operation", "name"),)
