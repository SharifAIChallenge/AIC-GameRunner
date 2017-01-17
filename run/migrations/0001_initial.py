# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-01-17 12:17
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('storage', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='FilePath',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_input', models.BooleanField()),
                ('file', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='storage.File')),
            ],
        ),
        migrations.CreateModel(
            name='Run',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('request_time', models.DateTimeField(auto_now_add=True, null=True)),
                ('start_time', models.DateTimeField(null=True)),
                ('end_time', models.DateTimeField(null=True)),
                ('log', models.TextField()),
                ('status', models.SmallIntegerField(choices=[(1, 'Success'), (2, 'Failure'), (3, 'Pending')], default=3)),
                ('owner', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='filepath',
            name='run',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='file_path_set', to='run.Run'),
        ),
    ]
