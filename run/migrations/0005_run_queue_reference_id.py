# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-11 19:50
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('run', '0004_auto_20170209_1645'),
    ]

    operations = [
        migrations.AddField(
            model_name='run',
            name='queue_reference_id',
            field=models.CharField(max_length=200, null=True),
        ),
    ]