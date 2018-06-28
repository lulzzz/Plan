# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-04-13 06:23
from __future__ import unicode_literals

import core.mixins_model
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_sourcing', '0006_auto_20180413_1105'),
    ]

    operations = [
        migrations.CreateModel(
            name='DimSample',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('report_file_name', models.CharField(max_length=100, unique=True)),
                ('image_relative_path', models.CharField(blank=True, max_length=500, null=True, verbose_name='image')),
                ('style', models.CharField(max_length=100, unique=True)),
                ('has_style', models.BooleanField(default=True)),
                ('article_number', models.CharField(blank=True, max_length=100, null=True)),
                ('result_status', models.CharField(blank=True, max_length=100, null=True)),
                ('overall_status', models.CharField(blank=True, max_length=100, null=True)),
                ('dim_vendor', models.CharField(blank=True, max_length=100, null=True)),
                ('sample_description', models.CharField(blank=True, max_length=100, null=True)),
                ('color', models.CharField(blank=True, max_length=100, null=True)),
                ('season_year', models.CharField(blank=True, max_length=100, null=True)),
                ('division', models.CharField(blank=True, max_length=100, null=True)),
                ('coo_fabric', models.CharField(blank=True, max_length=100, null=True)),
                ('coo_garment', models.CharField(blank=True, max_length=100, null=True)),
                ('agent', models.CharField(blank=True, max_length=100, null=True)),
                ('manufacturer', models.CharField(blank=True, max_length=100, null=True)),
                ('factory', models.CharField(blank=True, max_length=100, null=True)),
                ('mill', models.CharField(blank=True, max_length=100, null=True)),
                ('dye_type', models.CharField(blank=True, max_length=100, null=True)),
                ('test_type', models.CharField(blank=True, max_length=100, null=True)),
                ('thread_count', models.CharField(blank=True, max_length=100, null=True)),
                ('previous_report_number', models.CharField(blank=True, max_length=100, null=True)),
            ],
            options={
                'verbose_name': 'Test Report',
            },
            bases=(models.Model, core.mixins_model.ModelFormFieldNames),
        ),
        migrations.AlterModelOptions(
            name='factallocationadhoc',
            options={'verbose_name': 'Allocation Ad-Hoc'},
        ),
    ]
