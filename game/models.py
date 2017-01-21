import uuid

# -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import ugettext_lazy as _

class Competition(models.Model):
    name = models.CharField(verbose_name=_('Name'), max_length=100)
    server = models.ForeignKey(to='game.DockerContainer', verbose_name=_('Server'), null=False, blank=False)
    additional_containers = models.ManyToManyField('game.DockerContainer', verbose_name=_("additional containers"),
                                                   related_name='+', blank=True)

class Game(models.Model):
    STATUS_VALUES = (
        (0, _('Queued')),
        (1, _('Running')),
        (2, _('Finished')),
        (3, _('Failed')),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    competition = models.ForeignKey(to='game.Competition', verbose_name=_('Competition'), null=False, blank=False)
    config = models.ForeignKey(to='storage.File', verbose_name=_('Game Configuration'), null=False, blank=False)
    status = models.PositiveSmallIntegerField(verbose_name=_('status'), choices=STATUS_VALUES, default=0)
    start = models.DateTimeField(verbose_name=_('Started At'), auto_now=True)
    end = models.DateTimeField(verbose_name=_('Ended At'), auto_now=True)
    time_limit = models.IntegerField(verbose_name=_('Time Limit (s)'))

    def __unicode__(self):
        return self.name

class Team(models.Model):
    name = models.CharField(verbose_name=_('Name'), max_length=50)
    game = models.ForeignKey(to='game.Game', verbose_name=_('Game'), related_name='+')
    code = models.ForeignKey(to='storage.File', verbose_name=_('Code'), related_name='+')
    data = models.ForeignKey(to='storage.File', verbose_name=_('Data'), related_name='+')
    lang = models.ForeignKey(to='game.CompetitionLanguage', verbose_name=_('Language'))

    def __unicode__(self):
        return self.name

class CompetitionLanguage(models.Model):
    name = models.CharField(verbose_name=_('title'), max_length=200)
    competition = models.ForeignKey(to='game.Competition', verbose_name=_('Competition'), null=False, blank=False)
    compile_container = models.ForeignKey('game.DockerContainer', verbose_name=_('Compile Container'), related_name='+',
                                          null=True, blank=True)
    execute_container = models.ForeignKey('game.DockerContainer', verbose_name=_('Execute Container'), related_name='+',
                                          null=True, blank=True)

    def __unicode__(self):
        return self.name

class DockerContainer(models.Model):
    tag = models.CharField(verbose_name=_('tag'), max_length=50, unique=True)
    description = models.TextField(verbose_name=_('description'), blank=True)
    dockerfile_src = models.FileField(verbose_name=_('dockerfile source'), upload_to='docker/dockerfiles', null=True, blank=True)
    version = models.PositiveSmallIntegerField(verbose_name=_('version'), default=1)
    cores = models.CommaSeparatedIntegerField(verbose_name=_('cores'), default=1024, max_length=512)
    memory = models.PositiveIntegerField(verbose_name=_('memory'), default=100 * 1024 * 1024)
    swap = models.PositiveIntegerField(verbose_name=_('swap'), default=0)
    build_log = models.TextField(verbose_name=_('build log'), blank=True)

    def __unicode__(self):
        return '%s:%d' % (self.tag, self.version)
