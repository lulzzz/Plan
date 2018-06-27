import os

from django.db import models

from core import mixins_model
from core import utils


class Metadata(models.Model, mixins_model.ModelFormFieldNames):
    r"""
    Model for storing file specific details
    """

    # Database related fields
    database_table = models.CharField(unique=True, max_length=100)
    sheet_name = models.CharField(max_length=100, blank=True, null=True)
    last_load_dt = models.DateTimeField(auto_now=True)

    # File related fields
    filename = models.CharField(max_length=100)
    rel_path = models.CharField(max_length=500, verbose_name='relative path')
    abs_path = models.CharField(max_length=500, verbose_name='absolute path')
    extension = models.CharField(max_length=30)
    size = models.IntegerField(default=0)
    last_modified_dt = models.DateTimeField(verbose_name='last modified date')
    last_modified_by = models.CharField(max_length=500, blank=True, null=True)
    creation_dt = models.DateTimeField(blank=True, null=True)
    created_by = models.CharField(max_length=500, blank=True, null=True)
    has_rule = models.BooleanField(default=True)
    row_number = models.IntegerField(default=0)
    col_number = models.IntegerField(default=0)

    form_field_list = [
        'database_table',
        'extension',
        'filename',
        'sheet_name',
        'last_modified_dt',
    ]

    class Meta:
        verbose_name = 'Metadata'


class MetadataPK(models.Model, mixins_model.ModelFormFieldNames):
    r"""
    Model for storing the primary keys of source files
    """
    metadata = models.ForeignKey(Metadata, on_delete=models.CASCADE)
    field_name = models.CharField(max_length=500)


class MetadataRule(models.Model, mixins_model.ModelFormFieldNames):
    r"""
    Model for storing the transformation rules for source files
    """
    metadata = models.ForeignKey(Metadata, on_delete=models.CASCADE)
    rule = models.PositiveIntegerField()
    position = models.PositiveIntegerField()
