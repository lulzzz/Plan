import json

from django.conf import settings as cp
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.db.utils import IntegrityError
from django.urls import reverse_lazy
from django.db.models import Count, Sum, Case, When, Value, IntegerField
from django.db.models import Q
from django.db.models.functions import Lower, Upper

from rest_framework import status # To return status codes
from rest_framework.views import APIView
from rest_framework.response import Response

from core import gcbvs
from core import utils
from core import mixins_view
from blocks import views

from . import models



class SourceExtractTable(views.TableRead):
    r"""
    View that shows the content of metadata (latest extracts)
    """

    model = models.Metadata
    order_by = '-last_modified_dt'
    format_list = [
        None,
        None,
        None,
        None,
        'datetime',
    ]


class RowChartAPI(views.ChartAPI):
    r'''
    View that provides the chart configuration and data
    '''

    def get(self, request, format=None, **kwargs):
        label_list = sorted(list(set(models.Metadata.objects.values_list('database_table', flat=True))), key=str.lower)
        data_list = list()
        for label in label_list:
            data_list.append(models.Metadata.objects.filter(
                database_table=label
            ).first().row_number)

        data = {
            'labels': label_list,
            'datasets': [
                {
                    'label': 'Number of Rows',
                    'data': data_list
                }
            ]
        }
        return JsonResponse(data, safe=False)


class ColChartAPI(views.ChartAPI):
    r'''
    View that provides the chart configuration and data
    '''

    def get(self, request, format=None, **kwargs):
        label_list = sorted(list(set(models.Metadata.objects.values_list('database_table', flat=True))), key=str.lower)
        data_list = list()
        for label in label_list:
            data_list.append(models.Metadata.objects.filter(
                database_table=label
            ).first().col_number)

        data = {
            'labels': label_list,
            'datasets': [
                {
                    'label': 'Number of Columns',
                    'data': data_list
                }
            ]
        }
        return JsonResponse(data, safe=False)


# class DemandComboChartAPI(views.ChartAPI):
#     r'''
#     View that provides the chart configuration and data
#     '''
#     # Variable definition
#     model = models.FactDemand
#     order_by = 'dim_date_month_xf__year_month'
#     aggregation = 'quantity'
#     aggregation_label = 'quantity'
#     aggregation_dict = {
#         'values': ['dim_demand_category__name', 'dim_date_month_xf__year_month',],
#         'logic': {
#             'units_sum': Sum('quantity'),
#         }
#     }
#     filter_dict = None
#
#     def return_value_or_zero(self, queryset_dict):
#         if queryset_dict.get('quantity__sum'):
#             return queryset_dict.get('quantity__sum')
#         return 0
#
#
#     def get(self, request, format=None, **kwargs):
#
#         # Set filter_dict
#         self.set_filter_dict()
#         label_list = sorted(list(set(models.FactDemand.objects.filter(**self.filter_dict).values_list('dim_date_month_xf__year_month', flat=True))), key=str.lower)
#         data_dict_direct_ship = ['Direct Ship']
#         data_dict_warehouse_replenishment = ['Warehouse Replenishment']
#         data_dict_forecast = ['Forecast']
#         data_dict_capacity = ['Capacity']
#
#         for label in label_list:
#             xf_month_filter_dict = self.filter_dict.copy()
#             xf_month_filter_dict['dim_date_month_xf__year_month'] = label
#             fact_demand = models.FactDemand.objects
#             fact_capacity = models.FactCapacity.objects.filter(**xf_month_filter_dict)
#
#             data_dict_direct_ship.append(self.return_value_or_zero(fact_demand.filter(
#                 **xf_month_filter_dict,
#                 **{'dim_demand_category__name': 'Direct Ship'}
#             ).aggregate(Sum('quantity'))))
#             data_dict_warehouse_replenishment.append(self.return_value_or_zero(fact_demand.filter(
#                 **xf_month_filter_dict,
#                 **{'dim_demand_category__name': 'Warehouse Replenishment'}
#             ).aggregate(Sum('quantity'))))
#             data_dict_forecast.append(self.return_value_or_zero(fact_demand.filter(
#                 **xf_month_filter_dict,
#                 **{'dim_demand_category__name': 'Forecast'}
#             ).aggregate(Sum('quantity'))))
#             data_dict_capacity.append(self.return_value_or_zero(fact_capacity.aggregate(Sum('quantity'))))
#
#         data_dict = {
#             'bindto': '.combochartjs',
#             'data': {
#                 'columns': [
#                     data_dict_direct_ship,
#                     data_dict_warehouse_replenishment,
#                     data_dict_forecast,
#                     data_dict_capacity,
#                 ],
#                 'type': 'bar',
#                 'types': {
#                     'Capacity': 'spline',
#                 },
#                 'groups': [
#                     [data_dict_direct_ship[0], data_dict_warehouse_replenishment[0], data_dict_forecast[0]]
#                 ],
#                 'colors': {
#                     'Direct Ship': '#254e93',
#                     'Warehouse Replenishment': '#7fc97f',
#                     'Forecast': '#c11e1e',
#                     'Capacity': '#252126',
#                 },
#             },
#             'axis': {
#                 'x': {
#                     'type': 'category',
#                     'categories': label_list
#                 }
#             }
#         }
#
#         return JsonResponse(data_dict, safe=False)
#
#
#     def set_filter_dict(self):
#         # vendor
#         if self.kwargs.get('category') == 'dim_production_line':
#             # pk
#             if self.kwargs.get('pk'):
#                 self.filter_dict['dim_production_line__exact'] = self.kwargs.get('pk')
#
#         # product
#         elif self.kwargs.get('category') == 'dim_product':
#             # pk
#             if self.kwargs.get('pk'):
#                 self.filter_dict['dim_product_id__exact'] = self.kwargs.get('pk')
#             # keyword
#             elif self.kwargs.get('keyword'):
#                 query = (Q(dim_product__is_placeholder=False) & \
#                     (
#                         Q(dim_product__material=self.kwargs.get('keyword')) |
#                         Q(dim_product__material_text_short=self.kwargs.get('keyword')) |
#                         Q(dim_product__family=self.kwargs.get('keyword')) |
#                         Q(dim_product__group_description=self.kwargs.get('keyword'))
#                     )
#                 )
#                 self.filter_dict = query
