import os
from datetime import date

from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.conf import settings as cp
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.db.models import Count
from django.db.models import Sum
from django.db.models import Q
from django.db.models.functions import Lower, Upper

from rest_framework import status # To return status codes
from rest_framework.views import APIView
from rest_framework.response import Response

from blocks import views
from core import utils
from core import mixins_view

from apps.standards.app_console import mixins_apiview

from . import models
from . import forms
from . import serializers


class MasterTableAPI(mixins_apiview.MasterTableAPIMixin):
    r"""
    View that updates the master table specified in the request.
    Assuming user group has required permissions.
    """

    def get_model_obj(self):
        return eval('models.' + self.model_name)

    def get_serializer_obj(self):
        return eval('serializers.' + self.model_name + 'Serializer')


class MasterTableHeaderAPI(mixins_apiview.MasterTableHeaderAPIMixin):
    r"""
    View that loads the table header
    Assuming user group has required permissions.
    """

    def get_model_obj(self):
        return eval('models.' + self.model_name)

    def get_serializer_obj(self):
        return eval('serializers.' + self.model_name + 'Serializer')


class AllocationByGenderAPI(APIView):
    r'''
    View that provides the chart configuration and data
    '''

    def get(self, request, format=None, **kwargs):
        label_list = sorted(list(set(models.DimProductGender.objects.values_list('name', flat=True))), key=str.lower)
        data_list_confirmed = list()
        data_list_non_confirmed = list()
        for label in label_list:
            product_style_count = models.DimProduct.objects.filter(dim_product_gender__name=label).count()
            allocated_style_count = models.DimProduct.objects.filter(
                dim_product_gender__name=label,
                is_approved=True
            ).count()
            non_allocated_style_count = product_style_count - allocated_style_count
            data_list_confirmed.append(allocated_style_count)
            data_list_non_confirmed.append(non_allocated_style_count)

        data = {
            'labels': label_list,
            'datasets': [
                {
                    'label': 'Confirmed',
                    'data': data_list_confirmed,
                    'backgroundColor': ['#27d160' for x in list(range(len(label_list)))],
                    'borderColor': ['#0a5623' for x in list(range(len(label_list)))],
                    'borderWidth': 2
                },
                {
                    'label': 'Non-Confirmed',
                    'data': data_list_non_confirmed,
                    'backgroundColor': ['#c45850' for x in list(range(len(label_list)))],
                    'borderColor': ['#701d17' for x in list(range(len(label_list)))],
                    'borderWidth': 2
                }
            ]
        }

        return JsonResponse(data, safe=False)


class AllocationByProductTypeAPI(APIView):
    r'''
    View that provides the chart configuration and data
    '''

    def get(self, request, format=None, **kwargs):
        label_list = sorted(list(set(models.DimProductType.objects.values_list('name', flat=True))), key=str.lower)
        data_list_confirmed = list()
        data_list_non_confirmed = list()
        for label in label_list:
            product_style_count = models.DimProduct.objects.filter(dim_product_type__name=label).count()
            allocated_style_count = models.DimProduct.objects.filter(
                dim_product_type__name=label,
                is_approved=True
            ).count()
            non_allocated_style_count = product_style_count - allocated_style_count
            data_list_confirmed.append(allocated_style_count)
            data_list_non_confirmed.append(non_allocated_style_count)

        data = {
            'labels': label_list,
            'datasets': [
                {
                    'label': 'Confirmed',
                    'data': data_list_confirmed,
                    'backgroundColor': ['#27d160' for x in list(range(len(label_list)))],
                    'borderColor': ['#0a5623' for x in list(range(len(label_list)))],
                    'borderWidth': 2
                },
                {
                    'label': 'Non-Confirmed',
                    'data': data_list_non_confirmed,
                    'backgroundColor': ['#c45850' for x in list(range(len(label_list)))],
                    'borderColor': ['#701d17' for x in list(range(len(label_list)))],
                    'borderWidth': 2
                }
            ]
        }

        return JsonResponse(data, safe=False)


class VendorMapAPI(views.WorldMap):
    r"""
    View that shows the vendors counts on a worldmap (data)
    """

    def get(self, request, format=None, **kwargs):

        if self.kwargs.get('pk'):
            model_obj = models.DimVendor.objects.filter(pk=self.kwargs.get('pk')).get()
            country = model_obj.dim_location.country_code_a2.lower()
            label_list = [country]
            data_dict = dict()
            data_dict[country] = str(1)
        else:
            label_list = sorted(list(set(models.DimVendor.objects.values_list('dim_location__country_code_a2', flat=True))), key=str.lower)
            label_list = [x.lower() for x in label_list]
            data_dict = dict()
            for label in label_list:
                data_dict[label] = str(models.DimVendor.objects.filter(dim_location__country_code_a2=label).count())

        return JsonResponse(data_dict, safe=False)
