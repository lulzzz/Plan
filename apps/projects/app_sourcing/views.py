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


class AllocationByPriorityAPI(APIView):
    r'''
    View that provides the chart configuration and data
    '''

    def get(self, request, format=None, **kwargs):
        label_list = ["Exact Match", "Second-level Match", "Third-level Match", "Fourth-level Match", "Fifth-level Match"]

        data_list = list()
        for label in label_list:
            label_count = models.FactAllocation.objects.filter(
                matching_level=label,
                is_approved=False,
            ).values('dim_product').distinct().count()
            data_list.append(label_count)

        data = {
            'labels': label_list,
            'datasets': [
                {
                    'label': "Number of Matches",
                    'backgroundColor': ["#3e95cd", "#8e5ea2","#3cba9f","#e8c3b9","#c45850"],
                    'data': data_list
                }
            ]
        }
        return JsonResponse(data, safe=False)



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


class AllocationByCOOAPI(APIView):
    r'''
    View that provides the chart configuration and data
    '''

    def get(self, request, format=None, **kwargs):
        label_list = sorted(list(set(models.DimVendor.objects.exclude(is_active=False).values_list('dim_location__country', flat=True))), key=str.lower)
        data_list = list()
        for label in label_list:
            data_list.append(models.DimProduct.objects.filter(
                dim_vendor__dim_location__country=label,
                is_approved=True
            ).count())

        data = {
            'labels': label_list,
            'datasets': [
                {
                    'label': 'Number of Allocated Styles',
                    'data': data_list
                }
            ]
        }
        return JsonResponse(data, safe=False)


class ProductsByCustomerAPI(APIView):
    r'''
    View that provides the chart configuration and data
    '''

    def get(self, request, format=None, **kwargs):
        label_list = sorted(list(set(models.DimCustomer.objects.values_list('name', flat=True))), key=str.lower)
        data_list_confirmed = list()
        data_list_non_confirmed = list()
        for label in label_list:
            product_style_count = models.DimProduct.objects.filter(dim_customer__name=label).count()
            allocated_style_count = models.DimProduct.objects.filter(
                dim_customer__name=label,
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


class AllocationByVendorConfirmed(views.TableRead):
    r"""
    View that shows the content of the table (aggregated by vendor)
    """

    model = models.DimProduct
    filter_dict = { 'is_approved' + '__' + 'exact': True }
    header_list = ['vendor', 'country', 'styles allocated']
    aggregation_dict = {
        'values': ['dim_vendor__name', 'dim_vendor__dim_location__country'],
        'logic': {
            'style_count': Count('style'),
        }
    }
    format_list = [None, None, 'intcomma_rounding0',]
    tfoot = '2'


class AllocationByVendorNonConfirmed(views.TableRead):
    r"""
    View that shows the content of the table (aggregated by vendor)
    """

    model = models.DimProduct
    filter_dict = { 'is_approved' + '__' + 'exact': False }
    header_list = ['vendor', 'country', 'style recs']
    aggregation_dict = {
        'values': ['dim_vendor__name', 'dim_vendor__dim_location__country'],
        'logic': {
            'style_count': Count('style'),
        }
    }
    format_list = [None, None, 'intcomma_rounding0']
    tfoot = '2'


class AllocationSpecificProduct(views.TableRead):
    r"""
    View that shows the content of the table
    """

    model = models.FactAllocation
    limit = 250
    bulk_action = 'radiobox'
    js_list = [
        'init_data_table_control',
        'init_checkbox_control',
    ]
    header_list = [
        'choice',
        'new product',
        'matched product',
        'style',
        'silhouette',
        'product type',
        'similarity',
        'matching logic',
        'vendor',
        'FOB (USD)'
    ]
    format_list = [
        'radiobox',
        'image_link',
        'image_link',
        None,
        None,
        None,
        'percentagemultiplied',
        None,
        None,
        None,
    ]
    form_field_list = [
        'radiobox',
        [
            'dim_product',
            [
                'image_link',
            ],
        ],
        [
            'dim_product_matching',
            [
                'image_link',
                'style',
                'silhouette',
                [
                    'dim_product_type',
                    [
                        'name',
                    ],
                ],
            ],
        ],
        'similarity',
        'matching_logic',
        [
            'dim_vendor',
            [
                'code',
            ],
        ],
        'fob',
    ]

    def set_preselected_list(self):
        self.preselected_list = sorted(list(set(self.model.objects.filter(
            dim_product__id=self.pk,
            is_selected=True,
        ).values_list('id', flat=True))))

    def set_filter_dict(self):
        query = Q(dim_product__id=self.pk)
        self.filter_dict = query


class MatchingProductSelection(views.SimpleUpdate):
    r"""
    View that updates the matching product for a new product
    """
    model = models.FactAllocation

    def business_logic(self):
        pk = self.kwargs.get('pk', None)
        dim_product_id = int(self.kwargs.get('dim_product_id', 0))
        dim_product_matching_id = int(self.kwargs.get('dim_product_matching_id', 0))

        fact_row = self.model.objects.filter(
            pk=pk
        ).get()

        fact_group = self.model.objects.filter(
            dim_product__id=dim_product_id
        ).all()

        valid_dim_product_matching_id_list = list(set(fact_group.values_list('dim_product_matching_id', flat=True)))
        if dim_product_matching_id in valid_dim_product_matching_id_list:
            fact_group.update(is_selected=False)

            fact_row.is_selected = True
            fact_row.save()
            return True
        else:
            print('no')

        return False


class AllocationNonConfirmed(views.TableRead):
    r"""
    View that shows the content of the table
    """

    model = models.FactAllocation
    limit = 250
    order_by = 'matching_level'
    header_list = ['new product', 'matched product', 'style', 'silhouette', 'vendor', 'matching logic', 'matching level']
    format_list = ['image_link', 'image_link', None, None, None, None, None]
    form_field_list = [
        [
            'dim_product',
            [
                'image_link',
            ],
        ],
        [
            'dim_product_matching',
            [
                'image_link',
                'style',
                'silhouette',
            ],
        ],
        [
            'dim_vendor',
            [
                'code',
            ],
        ],
        'matching_logic',
        'matching_level',
    ]

    def set_filter_dict(self):
        self.filter_dict = {
            'dim_product__is_selected' + '__' + 'exact': False,
        }

        approved_product_id_list = list(set(models.FactAllocation.objects.filter(
            is_approved=True,
        ).values_list('dim_product_id', flat=True)))
        self.exclude_dict = {
            'dim_product_id' + '__' + 'in': approved_product_id_list
        }


class AllocationConfirmed(views.TableRead):
    r"""
    View that shows the content of the table (all)
    """

    model = models.DimProduct
    filter_dict = {
        'is_approved' + '__' + 'exact': False,
        'is_selected' + '__' + 'exact': True
    }
    limit = 250
    format_list = ['image_link',    None,       None,           None,       None,]
    header_list = ['image',         'style',    'silhouette',   'vendor',   'FOB',]
    form_field_list = [
        'image_link',
        'style',
        'silhouette',
        [
            'dim_vendor',
            [
                'code',
            ],
        ],
        'fob',
    ]


class AllocationConfirmedXTS(views.TableRead):
    r"""
    View that shows the content of the table (all)
    """

    model = models.FactAllocation
    filter_dict = {
        'is_approved' + '__' + 'exact': True,
        'allocation_type' + '__' + 'exact': 'XTS',
    }
    limit = 100
    format_list = ['image_link',    None,       None,           None,       None,           None,   'intcomma_rounding0']
    header_list = ['image',         'style',    'silhouette',   'vendor',   'ship date',    'FOB',  'quantity']
    form_field_list = [
        [
            'dim_product',
            [
                'image_link',
                'style',
                'silhouette',
            ],
        ],
        [
            'dim_vendor',
            [
                'code',
            ],
        ],
        'ship_date',
        'fob',
        'quantity',
    ]


class AllocationConfirmedXTSVendor(views.TableRead):
    r"""
    View that shows the content of the table (vendor)
    """

    model = models.DimProduct
    limit = 100
    format_list = ['image_link',    None,       None,           None,       None,]
    header_list = ['image',         'style',    'silhouette',   'vendor',   'FOB',]
    form_field_list = [
        'image_link',
        'style',
        'silhouette',
        [
            'dim_vendor',
            [
                'code',
            ],
        ],
        'fob',
    ]

    def set_filter_dict(self):
        self.filter_dict = {
            'is_approved' + '__' + 'exact': True,
            'dim_vendor_id' + '__' + 'exact': self.pk,
        }


class SearchResultProduct(views.TableRead):
    r"""
    View that shows the content of the table
    """

    model = models.DimProduct
    limit = 250
    format_list = ['image_link', None, None, None, None, None, 'boolean', 'boolean']
    header_list = ['sketch', 'style', 'silhouette', 'gender', 'product type', 'customer', 'is_selected', 'is_approved']
    form_field_list = [
        'image_link',
        'style',
        'silhouette',
        [
            'dim_product_gender',
            [
                'name',
            ],
        ],
        [
            'dim_product_type',
            [
                'name',
            ],
        ],
        [
            'dim_customer',
            [
                'name',
            ],
        ],
        'is_selected',
        'is_approved',
    ]

    def set_filter_dict(self):
        query = Q(dim_product_type__name=self.keyword)
        query.add(Q(silhouette=self.keyword), Q.OR)
        query.add(Q(description=self.keyword), Q.OR)
        query.add(Q(dim_product_gender__name=self.keyword), Q.OR)
        query.add(Q(dim_product_class__name=self.keyword), Q.OR)
        query.add(Q(dim_product_subclass__name=self.keyword), Q.OR)
        query.add(Q(dim_customer__name=self.keyword), Q.OR)

        self.filter_dict = query


class SearchResultVendor(views.TableRead):
    r"""
    View that shows the content of the table
    """

    model = models.DimVendor
    limit = 250
    format_list = ['link', None, None, 'boolean', None, None, 'boolean', 'boolean']
    form_field_list = [
        'link',
        'code',
        'name',
        'is_active',
        [
            'dim_location',
            [
                'country',
                'region',
                'is_gsp_eligible',
                'is_tpp_eligible',
            ],
        ],
    ]

    def set_filter_dict(self):
        query = Q(dim_location__country=self.keyword)
        # query.add(Q(dim_product_type__description=self.keyword), Q.OR)

        self.filter_dict = query


class SearchResultSample(views.TableRead):
    r"""
    View that shows the content of the table
    """

    model = models.DimSample
    limit = 250
    format_list = ['link', 'image_link', None, None, None, None,]
    header_list = [
        'link',
        'image',
        'style',
        'article number',
        'color',
        'result status',
    ]
    form_field_list = [
        'link',
        'image_relative_path',
        'style',
        'article_number',
        'color',
        'result_status',
    ]


    def set_filter_dict(self):
        query = Q(report_file_name=self.keyword)
        query.add(Q(style=self.keyword), Q.OR)
        query.add(Q(article_number=self.keyword), Q.OR)
        query.add(Q(dim_vendor=self.keyword), Q.OR)
        query.add(Q(sample_description=self.keyword), Q.OR)
        query.add(Q(color=self.keyword), Q.OR)

        self.filter_dict = query


class ProductAttributeTableSelectedTrue(views.FormValidation):
    r"""
    View that shows/updates the product table
    """
    # Define variables
    form_class = forms.ProductSelectedTrueForm
    model = models.DimProduct


class ProductAttributeTableSelectedFalse(views.FormValidation):
    r"""
    View that shows/updates the product table
    """
    # Define variables
    form_class = forms.ProductSelectedFalseForm
    model = models.DimProduct


class VendorAttributeTable(views.FormValidation):
    r"""
    View that shows/updates the product table
    """
    form_class = forms.VendorForm
    model = models.DimVendor


class SampleAttributeTable(views.FormValidation):
    r"""
    View that shows/updates the product table
    """
    form_class = forms.SampleForm
    model = models.DimSample


class ProductImageGallery(views.MediaGallery):
    r"""
    View that shows the product images
    """

    def get_context_dict(self, request):

        # Query images
        query = models.DimProductImageAssociation.objects.filter(
            dim_product__id=self.pk
        ).all()

        image_list = list()
        for image in query:
            image_list.append({
                'label': image.category,
                'reference': image.relative_path,
            })

        return image_list


class SampleImageGallery(views.MediaGallery):
    r"""
    View that shows the sample images
    """

    def get_context_dict(self, request):

        # Query images
        query = models.DimSample.objects.filter(
            pk=self.pk
        ).all()

        image_list = list()
        for image in query:
            image_list.append({
                'label': image.style,
                'reference': image.image_relative_path,
            })

        return image_list


class VendorMap(views.WorldMap):
    r"""
    View that shows the vendors counts on a worldmap (map structure)
    """

    def get_context_dict(self, request):

        if self.kwargs.get('pk'):
            return {'height': '300'}

        label_list = sorted(list(set(models.DimVendor.objects.exclude(is_active=False).values_list('dim_location__country', flat=True))), key=str.lower)
        data_list = list()
        total = 0
        for label in label_list:
            label_count = models.DimVendor.objects.filter(dim_location__country=label).count()
            total += label_count
            data_list.append({
                'label': label,
                'value': '{:,}'.format(label_count),
            })

        return {
            'height': '280',
            'title': 'Number of vendors',
            'total': '{:,}'.format(total),
            'table_items': data_list
        }


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


class ProductAllocationMap(views.WorldMap):
    r"""
    View that shows the allocated product counts on a worldmap (map structure)
    """

    def get_context_dict(self, request):
        label_list = sorted(list(set(models.DimProduct.objects.values_list('dim_vendor__dim_location__country', flat=True))), key=str.lower)
        data_list = list()
        total = 0
        for label in label_list:
            label_count = models.DimProduct.objects.filter(
                dim_vendor__dim_location__country=label,
                is_approved=True
            ).count()
            total += label_count
            data_list.append({
                'label': label,
                'value': '{:,}'.format(label_count),
            })

        return {
            'height': '350',
            'title': 'Allocated styles',
            'total': '{:,}'.format(total),
            'table_items': data_list
        }


class ProductAllocationMapAPI(views.WorldMap):
    r"""
    View that shows the allocated product counts on a worldmap (data)
    """

    def get(self, request, format=None, **kwargs):
        label_list = sorted(list(set(models.DimProduct.objects.values_list('dim_vendor__dim_location__country_code_a2', flat=True))), key=str.lower)
        label_list = [x.lower() for x in label_list]
        data_dict = dict()
        for label in label_list:
            data_dict[label] = str(models.DimProduct.objects.filter(
                dim_vendor__dim_location__country_code_a2__iexact=label
            ).count())

        return JsonResponse(data_dict, safe=False)


class ImageMatchingView(views.FormUpload):
    r"""
    View that shows the box for dragging image and PDF files for upload
    """
    pass


class ImageMatchingUpload(views.SimpleUpload):
    r"""
    View that processes the upload
    """

    form_class = forms.FileUploadForm
    model = models.UploadFile

    def post(self, request, **kwargs):
        form = self.form_class(request.POST, request.FILES)

        if form.is_valid():
            file_obj = request.FILES['file']

            # Upload file with Django
            new_file = self.model(file=file_obj)
            new_file.user = request.user
            new_file.extension = os.path.splitext(new_file.file.name)[1][1:].lower()
            new_file.save()

            # Check if PDF extraction is needed
            if new_file.extension == 'pdf':
                abs_path = os.path.join(cp.INPUT_DIRECTORY_PROJECT, 'images', new_file.file.name)

                # Extract first image from PDF
                file_property = {
                    'name': os.path.splitext(os.path.basename(new_file.file.name))[0],
                    'rel_path': new_file.file.name,
                    'abs_path': abs_path,
                    'extension': '.' + new_file.extension,
                }
                output_folder = os.path.dirname(abs_path)

                database_atoms = 0

                # Check if image was extracted correctly
                if len(database_atoms) > 0:
                    for database_atom in database_atoms:
                        print('atom', database_atom.get('source_master_component_reference'))
                        extracted_file_name = os.path.basename(database_atom.get('source_master_component_reference'))
                        extracted_file = self.model(file=models.upload_to(new_file, extracted_file_name))
                        extracted_file.user = request.user
                        extracted_file.extension = os.path.splitext(extracted_file.file.name)[1][1:].lower()
                        extracted_file.save()

                else:
                    return JsonResponse(False, safe=False)

            return JsonResponse(True, safe=False)

        return JsonResponse(form.errors, safe=False)


class ImageMatchingDisplay(views.PaginationView):
    r"""
    View that displays the uploaded image
    """

    paginate_by = 15
    order_by = 'id'
    order_type = '-' # - for desc
    model = models.UploadFile
    template_name = 'blocks/media_gallery.html'

    def get_context_dict(self, request):

        # Query images
        query = self.model.objects.filter(
            user=self.request.user,
        ).exclude(extension='pdf').order_by(self.order_type + self.order_by)[:self.paginate_by]

        # If user has uploaded an image before
        if query.exists():
            image_list = list()
            for idx, image in enumerate(query):
                image_list.append({
                    'id': image.id,
                    'label': os.path.basename(str(image.file)),
                    'text': image.created,
                    'reference': image.file,
                    'has_zoom': True,
                    # 'was_selected': True if idx == 0 else False
                })

            return image_list

        # If user has never uploaded an image
        else:
            return {
                'message': {
                    'text': 'No image uploaded',
                    'type': 'info',
                    'position_left': True,
                }
            }


class ImageMatchingResultTable(views.TableRead):
    r"""
    View that shows the content of the table
    """

    model = models.FactAllocationAdHoc
    limit = 250
    header_list = [
        'image',
        'style',
        'silhouette',
        'product type',
        'product class',
        'vendor',
        'COO',
        'similarity',
        'FOB (USD)',
        'quantity (units)'
    ]
    format_list = [
        'image_link',
        None,
        None,
        None,
        None,
        None,
        None,
        'percentagemultiplied',
        None,
        'intcomma_rounding0'
    ]

    def set_filter_dict(self):
        # Query latest image uploaded by user
        query = models.UploadFile.objects.filter(
            user=self.user
        ).exclude(extension='pdf')

        if self.pk:
            query = query.filter(pk=self.pk)

        # If user has uploaded an image before
        if query.exists():
            # Get uploaded_file
            uploaded_file = query.latest('id')

            # Get full file path for AI model
            abs_path = os.path.join(cp.INPUT_DIRECTORY_PROJECT, 'images', uploaded_file.file.name)

            # Execute AI model
            if not models.FactAllocationAdHoc.objects.filter(uploaded_file_id=uploaded_file.id).exists():
                pass

            filter_dict = { 'uploaded_file_id' + '__' + 'exact': uploaded_file.id }


        # If user has never uploaded an image
        else:
            filter_dict = { 'id' + '__' + 'exact': 0 }

        # Set filter_dict variable
        self.filter_dict = filter_dict



class SampleTestReportTable(views.TableRead):
    r"""
    View that shows the content of the table
    """

    model = models.FactTestReport
    limit = 250
    header_list = [
        'test',
        'successful?',
        'failed colorway',
    ]
    format_list = [
        None,
        'boolean',
        None,
    ]

    form_field_list = [
        [
            'dim_test',
            [
                'name',
            ],
        ],
        'is_successful',
        'failed_colorway',
    ]

    def set_filter_dict(self):
        # Set filter_dict variable
        self.filter_dict = { 'dim_sample_id' + '__' + 'exact': self.pk }



class QCReportPivotTable(views.PivotTableAPI):
    r"""
    View that shows the content of the pivot table
    """

    model = models.DimSample

    header_dict = {
        'style': 'style',
        'result_status': 'result status',
        'overall_status': 'overall status',
        'dim_vendor': 'vendor',
        'color': 'color',
        'season_year': 'season',
        'division': 'division',
        'coo_fabric': 'fabric COO',
        'coo_garment': 'garment COO',
        'agent': 'agent',
        'manufacturer': 'manufacturer',
        'factory': 'factory',
        'mill': 'mill',
        'dye_type': 'dye type',
        'test_type': 'test type',
        'thread_count': 'thread count',
        'previous_report_number': 'previous report number',
        'contract_weight': 'contract weight',
        'dye_print_method': 'dye/print method',
        'fabric_finish': 'fabric finish',
        'garment_finish': 'garment finish',
        'label_fiber_content': 'label fiber content',
        'mc_division': 'MC division',
        'mid': 'MID',
        'recommended_care_instructions': 'recommended care instructions',
        'recommended_fiber_content': 'recommended fiber content',
        'sample_with_luxury_fiber': 'sample with luxury fiber',
        'submitted_care_instructions': 'submitted care instructions',
        'yarn_size': 'yarn size',
        'report_file_name_count': 'test report count',
    }
    aggregation_dict = {
        'values': [
            'style',
            'result_status',
            'overall_status',
            'dim_vendor',
            'color',
            'season_year',
            'division',
            'coo_fabric',
            'coo_garment',
            'agent',
            'manufacturer',
            'factory',
            'mill',
            'dye_type',
            'test_type',
            'thread_count',
            'previous_report_number',
            'contract_weight',
            'dye_print_method',
            'fabric_finish',
            'garment_finish',
            'label_fiber_content',
            'mc_division',
            'mid',
            'recommended_care_instructions',
            'recommended_fiber_content',
            'sample_with_luxury_fiber',
            'submitted_care_instructions',
            'yarn_size',
        ],
        'logic': {
            'report_file_name_count': Count('report_file_name'),
        }
    }

    def set_filter_dict(self):
        self.filter_dict = dict()

    # # Return empty json with GET
    # def get(self, request, format=None, **kwargs):
    #     return JsonResponse([], safe=False)


class PassFailReportPivotTable(views.PivotTableAPI):
    r"""
    View that shows the content of the pivot table
    """

    model = models.FactTestReport

    header_dict = {
        'dim_sample__style': 'style',
        'dim_sample__color': 'color',
        'dim_sample__dim_vendor': 'vendor',
        'dim_test__name': 'test',
        'is_successful': 'successful?',
        'failed_colorway': 'failed colorway',
        'test_count': 'test count',
    }
    aggregation_dict = {
        'values': [
            'dim_sample__style',
            'dim_sample__color',
            'dim_sample__dim_vendor',
            'dim_test__name',
            'is_successful',
            'failed_colorway',
        ],
        'logic': {
            'test_count': Count('id'),
        }
    }

    def set_filter_dict(self):
        self.filter_dict = dict()
