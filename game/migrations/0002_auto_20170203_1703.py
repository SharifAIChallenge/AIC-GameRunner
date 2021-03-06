# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-03 17:03
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='operationparameter',
            old_name='input_parameter',
            new_name='is_input',
        ),
        migrations.AlterField(
            model_name='operationresource',
            name='file',
            field=models.FileField(upload_to='nfs/', verbose_name='file'),
        ),
        migrations.AlterField(
            model_name='operationparameter',
            name='is_input',
            field=models.BooleanField(verbose_name='is input?'),
        ),
    ]
