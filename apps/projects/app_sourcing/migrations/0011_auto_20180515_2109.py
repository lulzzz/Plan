# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-05-15 13:09
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app_sourcing', '0010_auto_20180515_2108'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='dimmaterial',
            unique_together=set([('fiber_content', 'fiber_construction', 'yarn_size')]),
        ),
    ]