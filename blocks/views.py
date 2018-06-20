import os

from django.core.exceptions import FieldDoesNotExist
from django.db.models import Count
from django.db.models import Sum
from django.db.models import Q
from django.db.models.functions import Lower, Upper
from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.conf import settings as cp

from rest_framework import status # To return status codes
from rest_framework.views import APIView
from django.http import JsonResponse

from core.gcbvs import BlockView
from core.gcbvs import SimpleView
from core.gcbvs import RPCView
from core.gcbvs import ExtendedListView
from core import utils


class MediaGallery(BlockView):
    r"""
    View that loads the media gallery block
    """
    # Define variables
    template_name = 'blocks/media_gallery.html'


class TableRead(BlockView):
    r"""
    View that loads the table read only block
    """
    # Define variables
    template_name = 'blocks/table_read.html'
    js_list = [
        'init_data_table_control',
    ]
    is_datatable = True
    order_by = 'id'
    exclude_dict = None
    aggregation_dict = None
    aggregation = None
    xaxis = None
    limit = 50000
    page_length = 10
    header_list = None
    form_field_list = None
    format_list = None # 'strong', 'intcomma', 'image', 'link', 'image_link', 'checkbox', 'radiobox', None
    bulk_action = False
    preselected_list = None
    tfoot = None
    post_amends_filter_dict = True

    delimiter = '|'

    def set_form_field_list(self):
        if self.form_field_list:
            self.form_field_list = self.form_field_list

    def set_filter_dict(self):
        pass

    def set_preselected_list(self):
        pass

    def post_action(self):
        pass

    def post_data_processing(self, request):
        # Read POST variables
        for key, values in request.POST.lists():
            if key != 'csrfmiddlewaretoken':
                if key == 'level':
                    if type(values) is list:
                        self.xaxis = values[0]
                    else:
                        self.xaxis = values
                elif key == 'aggregation':
                    self.aggregation = values[0]
                else:
                    # Skip empty lists
                    if len(values) == 1 and values[0] == '':
                        continue
                    # Handle tokenfields
                    if self.delimiter in values[0]:
                        values = values[0].split(self.delimiter)
                    self.post_filter_dict[key] = values

                    # Avoid overwriting filters if POST contains data to save
                    if self.post_amends_filter_dict:
                        self.filter_dict[key + '__in'] = values

        # actual post action
        self.post_action()

    def get_context_dict(self, request):
        # Get model
        model_obj = self.model

        # Data queryset
        data_list = list()

        # Filter
        self.set_filter_dict()
        if self.filter_dict:
            if type(self.filter_dict) is Q:
                queryset = model_obj.objects.filter(self.filter_dict)
            else:
                queryset = model_obj.objects.filter(**self.filter_dict)
                if self.exclude_dict:
                    queryset = queryset.exclude(**self.exclude_dict)
        else:
            queryset = model_obj.objects.all()

        # Field name list
        self.set_form_field_list()

        if self.form_field_list is None:
            field_names_list = model_obj.get_form_field_names_list(model_obj)
        else:
            field_names_list = self.form_field_list
        # checkbox
        self.preselected_list = list()
        self.set_preselected_list()

        # Check if table is empty
        if not queryset.exists():
            return {
                'message': {
                    'text': 'Table does not have data',
                    'type': 'info',
                    'position_left': True,
                }
            }

        # Aggregate case
        if self.aggregation_dict:
            queryset = queryset.values(*self.aggregation_dict['values'])
            queryset = queryset.annotate(**self.aggregation_dict['logic'])

            # Data queryset
            header_list = self.header_list
            data_list = utils.convert_list_of_dicts_into_list_of_lists(list(queryset)[:self.limit])

        # Non aggregation case
        else:
            # Ordering
            queryset = queryset.order_by(self.order_by)[:self.limit]

            # Model without related fields (flat)
            if utils.check_list_depth_flat(field_names_list):
                if not self.header_list:
                    try:
                        header_list = model_obj.get_form_field_names_verbose_list(model_obj)
                    except FieldDoesNotExist:
                        header_list = self.header_list

                for field_name_obj_level0 in queryset:
                    temp_list = list()
                    for h in field_names_list:
                        temp_list.append(getattr(field_name_obj_level0, h))
                    data_list.append(temp_list)

            # Model with related fields
            else:

                header_list = list()

                # Todo create generic function
                # Iterate through queryset
                for idx, field_name_obj_level0 in enumerate(queryset):
                    temp_list = list()

                    # Iterate through field_names_list
                    for field_name_obj_i1 in field_names_list:

                        field_name_obj_level1 = field_name_obj_i1

                        # LEVEL 1
                        # if the index is a string, get value out of queryset object
                        if type(field_name_obj_level1) is str:
                            if idx == 0:
                                if not self.header_list:
                                    try:
                                        header_list.append(field_name_obj_level0._meta.get_field(field_name_obj_level1).verbose_name) # header
                                    except FieldDoesNotExist:
                                        header_list.append(field_name_obj_level1)

                            field_name_obj_level1 = getattr(field_name_obj_level0, field_name_obj_level1)
                            temp_list.append(field_name_obj_level1) # data

                        # LEVEL 2 (field_name_obj_level1 is a list)
                        else:
                            field_name_obj_level1 = getattr(field_name_obj_level0, field_name_obj_i1[0]) # FeatureStoreInput
                            field_names_list_i2 = field_name_obj_i1[1] # feature_list

                            # Iterate through list
                            for field_name_obj_i2 in field_names_list_i2:

                                field_name_obj_level2 = field_name_obj_i2

                                # if the index is a string, get values out of queryset objects
                                if type(field_name_obj_level2) is str:
                                    if idx == 0:
                                        if not self.header_list:
                                            try:
                                                header_list.append(field_name_obj_level1._meta.get_field(field_name_obj_level2).verbose_name) # header
                                            except FieldDoesNotExist:
                                                header_list.append(field_name_obj_level2)

                                    field_name_obj_level2 = getattr(field_name_obj_level1, field_name_obj_level2)
                                    temp_list.append(field_name_obj_level2) # data

                                # LEVEL 3 (field_name_obj_level2 is a list)
                                else:
                                    field_name_obj_level2 = getattr(field_name_obj_level1, field_name_obj_i2[0]) # FeatureStoreInput
                                    field_names_list_i3 = field_name_obj_i2[1] # feature_list

                                    # Iterate through list
                                    for field_name_obj_i3 in field_names_list_i3:

                                        field_name_obj_level3 = field_name_obj_i3

                                        # if the index is a string, get values out of queryset objects
                                        if type(field_name_obj_level3) is str:
                                            if idx == 0:
                                                if not self.header_list:
                                                    try:
                                                        header_list.append(field_name_obj_level2._meta.get_field(field_name_obj_level3).verbose_name) # header
                                                    except FieldDoesNotExist:
                                                        header_list.append(field_name_obj_level3)

                                            field_name_obj_level3 = getattr(field_name_obj_level2, field_name_obj_level3)
                                            temp_list.append(field_name_obj_level3) # data


                    # Add row to data_list
                    data_list.append(temp_list)

        if self.header_list:
            header_list = self.header_list

        return {
            'header_list': header_list,
            'data_list': data_list,
            'format_list': self.format_list,
            'form_field_list': self.form_field_list,
            'bulk_action': self.bulk_action,
            'tfoot': self.tfoot,
            'page_length': self.page_length,
            'preselected_list': self.preselected_list,
            'is_datatable': self.is_datatable,
        }


class TableHandson(BlockView):
    r"""
    View that loads the table that uses the handson JS plugin
    """
    # Define variables
    template_name = 'blocks/table_handson.html'
    js_list = [
        'init_handson_table_control',
    ]


class TableProcedure(BlockView):
    r"""
    View that loads the table listing the stored procedures to be run within the database
    """
    # Define variables
    template_name = 'blocks/table_procedure.html'
    js_list = [
        'init_stored_procedure_control',
    ]


class WorldMap(BlockView):
    r"""
    View that loads the world map block
    """
    # Define variables
    template_name = 'blocks/worldmap.html'
    js_list = [
        'init_map_control',
    ]


class FormValidation(BlockView):
    r"""
    View that updates form
    """
    # Define variables
    template_name = 'blocks/form_validation_django.html'
    pk = None

    def get_context_dict(self, request):
        if self.pk is None:
            self.pk = self.kwargs.get('pk', 0)
        model = get_object_or_404(self.model, pk=self.pk)

        self.form_class = self.form_class(instance=model)
        return {
            'form_items': self.form_class
        }

    def post_data_processing(self, request):
        if self.pk is None:
            self.pk = self.kwargs.get('pk', 0)
        post = request.POST
        model_instance = self.model.objects.get(pk=self.pk)
        form = self.form_class(post, instance=model_instance)

        if form.is_valid():
            result = form.save(commit=False)
            result.save()

            # Process additional events
            self.post_data_processing_success_action(form)

            self.context_dict_additional['message'] = {
                'text': 'The form was successfully updated.',
                'type': 'success',
                'position_left': True,
            }
        else:
            self.context_dict_additional['form_items'] = form


    def post_data_processing_success_action(self, form):
        pass


class FormUpload(BlockView):
    r"""
    View that loads the html and JS structure (without data)
    """
    # Define variables
    template_name = 'blocks/form_upload.html'
    js_list = [
        'init_form_upload',
    ]


class ChartJS(BlockView):
    r"""
    View that loads the html and JS structure (without data)
    """
    # Define variables
    template_name = 'blocks/chartjs.html'
    js_list = [
        'init_chartjs_control',
    ]


class ComboChartJS(BlockView):
    r"""
    View that loads the html and JS structure (without data)
    """
    # Define variables
    template_name = 'blocks/combochartjs.html'
    js_list = [
        'init_combochartjs_control',
    ]


class PivotTableJS(BlockView):
    r"""
    View that loads the html and JS structure (without data)
    """
    # Define variables
    template_name = 'blocks/pivottable.html'
    js_list = [
        'init_pivottable_control',
    ]


class SimpleUpdate(SimpleView):
    r"""
    View that does a simple update according to pk and target field(s)
    """
    # Define variables
    model = None

    def business_logic(self, request=None):
        return True

    def get(self, request, **kwargs):
        return JsonResponse(self.business_logic(), safe=False)

    def post(self, request, **kwargs):
        return JsonResponse(self.business_logic(request=request), safe=False)


class SimpleUpload(SimpleView):
    r"""
    View that does a simple upload
    """
    # Define variables
    model = None
    form_class = None

    def get(self, request, **kwargs):
        return JsonResponse(True, safe=False)

    def post(self, request, **kwargs):
        form = self.form_class(request.POST, request.FILES)

        if form.is_valid():
            file_obj = request.FILES['file']

            # Upload file manually
            # utils.handle_uploaded_file('image_matching/', file_obj)

            # Upload file with Django
            new_file = self.model(file=file_obj)
            new_file.user = request.user
            new_file.extension = os.path.splitext(new_file.file.name)[1][1:].lower()
            new_file.save()
            return JsonResponse(True, safe=False)

        return JsonResponse(form.errors, safe=False)


class SimpleRPC(RPCView):
    r"""
    View that does a simple RPC call
    """
    pass


class ChartAPI(APIView):
    r'''
    View that provides the chart configuration and data
    '''
    # Variable definition
    model = None
    order_by = None
    xaxis = None
    chart_label = ''
    aggregation = None
    aggregation_label = ''
    filter_dict = None
    delimiter = '|'

    # Overwrite variables
    def __init__(self):
        super(APIView, self).__init__()
        self.filter_dict = dict()

    def post(self, request, format=None, **kwargs):

        # Read POST variables
        for key, values in request.POST.lists():
            if key != 'csrfmiddlewaretoken':
                if key == 'level':
                    self.xaxis = values[0]
                elif key == 'aggregation':
                    self.aggregation = values[0]
                else:
                    # Skip empty lists
                    if len(values) == 1 and values[0] == '':
                        continue
                    # Handle tokenfields
                    if self.delimiter in values[0]:
                        values = values[0].split(self.delimiter)
                    self.filter_dict[key + '__in'] = values

        return JsonResponse(self.get_display_data(), safe=False)

    def get(self, request, format=None, **kwargs):
        # Get aggregation from kwargs
        if self.kwargs.get('aggregation') == 'salesvalue':
            self.aggregation = 'salesvalue'

        return JsonResponse(self.get_display_data(), safe=False)

    def set_filter_dict(self):
        pass

    def additional_list_logic(self, label_list, data_list):
        return label_list, data_list

    def get_display_data(self):

        # Get PK entries
        if self.kwargs.get('pk') and self.kwargs.get('category'):
            self.filter_dict[self.kwargs.get('category') + '__exact'] = self.kwargs.get('pk')

        # Extend filter_dict
        self.set_filter_dict()

        # Big table query
        if type(self.filter_dict) is Q:
            queryset = self.model.objects.filter(self.filter_dict)
        else:
            queryset = self.model.objects.filter(**self.filter_dict)

        data_list_query = queryset.values(
            self.xaxis
        ).annotate(
            aggregation_sum=Sum(self.aggregation)
        ).order_by(self.order_by)

        label_list = list()
        data_list = list()
        for data_dict in list(data_list_query):
            label_list.append(data_dict.get(self.xaxis))
            data_list.append(data_dict.get('aggregation_sum'))

        # Apply additional logic to lists
        label_list, data_list = self.additional_list_logic(label_list, data_list)

        data = {
            'labels': label_list,
            'datasets': [
                {
                    'label': self.chart_label + ' ({})'.format(str(self.aggregation_label if self.aggregation_label else self.aggregation)),
                    'data': data_list
                }
            ]
        }
        return data



class PivotTableAPI(APIView):
    r'''
    View that provides the pivot table configuration and data
    '''
    # Variable definition
    model = None
    aggregation = None
    filter_dict = None
    header_dict = None
    delimiter = '|'

    def post(self, request, format=None, **kwargs):
        # Init filter dicts
        if self.filter_dict is None:
            self.filter_dict = dict()

        # Read POST variables
        for key, values in request.POST.lists():
            if key != 'csrfmiddlewaretoken':
                # Skip empty lists
                if len(values) == 1 and values[0] == '':
                    continue
                # Handle tokenfields
                if self.delimiter in values[0]:
                    values = values[0].split(self.delimiter)
                self.filter_dict[key + '__in'] = values

        return JsonResponse(self.get_display_data(), safe=False)

    def get(self, request, format=None, **kwargs):
        return JsonResponse(self.get_display_data(), safe=False)

    def set_filter_dict(self):
        pass

    def get_display_data(self):
        # Add pre-defined filter
        self.set_filter_dict()

        # Perform aggregation and filtering
        queryset = self.model.objects.filter(**self.filter_dict)
        queryset = queryset.values(*self.aggregation_dict['values'])
        queryset = queryset.annotate(**self.aggregation_dict['logic'])

        return_list = list()
        for row in list(queryset):
            temp_dict = dict()
            for key, value in self.header_dict.items():
                temp_dict[value] = row[key]
            return_list.append(temp_dict)

        return return_list


class TokenFieldAPI(APIView):
    r"""
    View that loads the data for tokenfield.
    Get request only.
    """
    model = None
    filter_dict = None
    field_name = None
    limit=15

    def get(self, request, format=None, **kwargs):
        # Prepare result serializer
        serializer_combined = list()

        # Try getting parameter from URL
        query = self.kwargs.get('query', None)

        # Get parameter from GET
        if query is None:
            query = request.GET.get('term', '').replace('+', ' ')

        # Add pre-defined filter
        self.set_filter_dict()

        # Integrate search parameter
        self.filter_dict[self.field_name + '__icontains'] = query

        # Perform filtering
        queryset = self.model.objects.filter(**self.filter_dict)
        queryset = queryset.order_by(self.field_name)
        queryset = queryset.values_list(self.field_name, flat=True).distinct()[:self.limit]
        queryset = list(queryset)

        return JsonResponse(queryset, safe=False)

    def set_filter_dict(self):
        if self.filter_dict is None:
            self.filter_dict = dict()


class PaginationView(BlockView):
    r"""
    View that loads the BlockView with a custom paginator (not Django one)
    """
    # Define variables
    paginate_by = 10
    js_list = [
        'init_paginator_control',
    ]


class SimpleBlockView(BlockView):
    r"""
    View that loads the Simple BlockView
    """
    # Define variables
    test = True


class TreeView(BlockView):
    r"""
    View that loads a decision tree
    """
    # Define variables
    template_name = 'blocks/tree.html'
    js_list = [
        'init_jstree_control',
    ]
