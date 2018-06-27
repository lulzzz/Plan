# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-06-27 08:42
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_pipeline', '0007_auto_20180613_1614'),
    ]

    operations = [
        migrations.AddField(
            model_name='metadata',
            name='col_number',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='metadata',
            name='row_number',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='metadata',
            name='abs_path',
            field=models.CharField(max_length=500, verbose_name='absolute path'),
        ),
        migrations.AlterField(
            model_name='metadata',
            name='last_modified_dt',
            field=models.DateTimeField(verbose_name='last modified date'),
        ),
        migrations.AlterField(
            model_name='metadata',
            name='rel_path',
            field=models.CharField(max_length=500, verbose_name='relative path'),
        ),
    ]