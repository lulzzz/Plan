# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-04-13 06:35
from __future__ import unicode_literals

import core.mixins_model
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app_sourcing', '0007_auto_20180413_1423'),
    ]

    operations = [
        migrations.CreateModel(
            name='DimTest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
            ],
            options={
                'verbose_name': 'Test Master',
            },
            bases=(models.Model, core.mixins_model.ModelFormFieldNames),
        ),
        migrations.CreateModel(
            name='FactTestReport',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_successful', models.BooleanField(default=False)),
                ('failed_colorway', models.CharField(max_length=100, unique=True)),
                ('dim_sample', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='app_sourcing.DimSample')),
                ('dim_test', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='app_sourcing.DimTest')),
            ],
            options={
                'verbose_name': 'Test Report',
            },
            bases=(models.Model, core.mixins_model.ModelFormFieldNames),
        ),
    ]
