# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-04 16:11
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0002_auto_20170203_1703'),
        ('run', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ParameterValue',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('_value', models.TextField()),
                ('parameter', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='game.OperationParameter')),
                ('run', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='parameter_value_set', to='run.Run')),
            ],
        ),
        migrations.RemoveField(
            model_name='filepath',
            name='file',
        ),
        migrations.RemoveField(
            model_name='filepath',
            name='run',
        ),
        migrations.DeleteModel(
            name='FilePath',
        ),
    ]
