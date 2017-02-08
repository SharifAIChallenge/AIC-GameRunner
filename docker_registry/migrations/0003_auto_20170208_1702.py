# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2017-02-08 17:02
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('docker_registry', '0002_auto_20170206_2253'),
    ]

    operations = [
        migrations.AddField(
            model_name='dockerfile',
            name='latest_image_version',
            field=models.IntegerField(default=0, editable=False),
        ),
        migrations.AlterField(
            model_name='dockerfile',
            name='version',
            field=models.IntegerField(editable=False),
        ),
    ]