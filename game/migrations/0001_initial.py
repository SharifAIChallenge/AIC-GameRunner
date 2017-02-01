# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-01-21 03:24
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('storage', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Competition',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Name')),
            ],
        ),
        migrations.CreateModel(
            name='CompetitionLanguage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, verbose_name='title')),
                ('competition', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='game.Competition', verbose_name='Competition')),
            ],
        ),
        migrations.CreateModel(
            name='DockerContainer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tag', models.CharField(max_length=50, unique=True, verbose_name='tag')),
                ('description', models.TextField(blank=True, verbose_name='description')),
                ('dockerfile_src', models.FileField(blank=True, null=True, upload_to='docker/dockerfiles', verbose_name='dockerfile source')),
                ('version', models.PositiveSmallIntegerField(default=1, verbose_name='version')),
                ('cores', models.CommaSeparatedIntegerField(default=1024, max_length=512, verbose_name='cores')),
                ('memory', models.PositiveIntegerField(default=104857600, verbose_name='memory')),
                ('swap', models.PositiveIntegerField(default=0, verbose_name='swap')),
                ('build_log', models.TextField(blank=True, verbose_name='build log')),
            ],
        ),
        migrations.CreateModel(
            name='Game',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('status', models.PositiveSmallIntegerField(choices=[(0, 'Queued'), (1, 'Running'), (2, 'Finished'), (3, 'Failed')], default=0, verbose_name='status')),
                ('start', models.DateTimeField(auto_now=True, verbose_name='Started At')),
                ('end', models.DateTimeField(auto_now=True, verbose_name='Ended At')),
                ('time_limit', models.IntegerField(verbose_name='Time Limit (s)')),
                ('competition', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='game.Competition', verbose_name='Competition')),
                ('config', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='storage.File', verbose_name='Game Configuration')),
            ],
        ),
        migrations.CreateModel(
            name='Team',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, verbose_name='Name')),
                ('code', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='storage.File', verbose_name='Code')),
                ('data', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='storage.File', verbose_name='Data')),
                ('game', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='game.Game', verbose_name='Game')),
                ('lang', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='game.CompetitionLanguage', verbose_name='Language')),
            ],
        ),
        migrations.AddField(
            model_name='competitionlanguage',
            name='compile_container',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='game.DockerContainer', verbose_name='Compile Container'),
        ),
        migrations.AddField(
            model_name='competitionlanguage',
            name='execute_container',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='game.DockerContainer', verbose_name='Execute Container'),
        ),
        migrations.AddField(
            model_name='competition',
            name='additional_containers',
            field=models.ManyToManyField(blank=True, related_name='_competition_additional_containers_+', to='game.DockerContainer', verbose_name='additional containers'),
        ),
        migrations.AddField(
            model_name='competition',
            name='server',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='game.DockerContainer', verbose_name='Server'),
        ),
    ]