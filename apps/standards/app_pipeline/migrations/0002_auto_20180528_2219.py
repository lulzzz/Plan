# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-05-28 14:19
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app_pipeline', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='metadata',
            old_name='absolute_path',
            new_name='abs_path',
        ),
        migrations.RenameField(
            model_name='metadata',
            old_name='relative_path',
            new_name='rel_path',
        ),
    ]
