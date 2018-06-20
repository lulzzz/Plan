import os

from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.conf import settings as cp
from django.urls import reverse_lazy

from core.gcbvs import LoginEnvironmentView
from core.gcbvs import ContentView
from core.gcbvs import DefaultView
from core import utils
from core import mixins_view

from apps.standards.app_console.models import UserPermissions
from apps.standards.app_console.models import GroupPermissions
from apps.standards.app_console.models import Item

from apps.projects.app_sourcing import models


class BaseView(LoginEnvironmentView, mixins_view.SecurityModelNameMixin):
    r"""
    View that loads the base application structure after user authentication
    """
    # Define variables
    template_name = 'architecture/application_structure.html'
    user_permission_model = UserPermissions
    group_permission_model = GroupPermissions
    permission_type = 'table'
    target_model = Item

    def get(self, request):

        # Get model name list
        self.set_user(request.user)
        model_name_list = self.get_authorized_model_item_list()

        master_table_list = list()
        for model_name in model_name_list:
            model_obj = eval('models.' + model_name)

            master_table_list.append({
                'name': model_name.lower(),
                'label': model_obj._meta.verbose_name,
                'url': reverse_lazy('master_table_tab', kwargs={'item': model_name}).replace('/', '#', 1),
            })

        # Prepare template data
        side_menu_dict = dict()
        side_menu_dict['groups'] = [
            {
                'name': 'General',
                'values':
                [
                    {
                        'name': 'dashboard_tab',
                        'label': 'Dashboard',
                        'icon': 'fa-dashboard',
                        'url': reverse_lazy('dashboard_tab').replace('/', '#', 1),
                        'values': None,
                    },
                    {
                        'name': 'image_matching_tab',
                        'label': 'Image Matching',
                        'icon': 'fa-file-image-o',
                        'url': reverse_lazy('image_matching_tab').replace('/', '#', 1),
                        'values': None,
                    },
                    {
                        'name': 'operations',
                        'label': 'Operations',
                        'icon': 'fa-pencil',
                        'values':
                        [
                            {
                                'name': 'product_allocation_tab',
                                'label': 'Recommended Allocations',
                                'url': reverse_lazy('product_allocation_tab').replace('/', '#', 1)
                            },
                            {
                                'name': 'product_allocation_confirmed_tab',
                                'label': 'Confirmed Allocations',
                                'url': reverse_lazy('product_allocation_confirmed_tab').replace('/', '#', 1)
                            },
                            # {
                            #     'name': 'product_allocation_confirmed_xts_tab',
                            #     'label': 'Confirmed Allocations in XTS',
                            #     'url': reverse_lazy('product_allocation_confirmed_xts_tab').replace('/', '#', 1)
                            # },
                        ]
                    },
                    {
                        'menu_item': 'search',
                        'name': 'search_tab',
                        'label': 'Search Results',
                        'icon': 'fa-search',
                        'url': reverse_lazy('search_tab').replace('/', '#', 1),
                        'values': None,
                    },
                ],
            },
            {
                'name': 'Test Reports',
                'values':
                [
                    {
                        'name': 'qc_report_tab',
                        'label': 'QC Report',
                        'icon': 'fa-paper-plane-o',
                        'url': reverse_lazy('qc_report_tab').replace('/', '#', 1),
                        'values': None,
                    },
                ]
            },
        ]

        if len(master_table_list) > 0:
            side_menu_dict['groups'].append(
                {
                    'name': 'Super User',
                    'values':
                    [
                        {
                            'name': 'master_table',
                            'label': 'Master Tables',
                            'icon': 'fa-table',
                            'url': '',
                            'values': master_table_list,
                        },
                    ]
                }
            )



        settings_dropdown_list = [
            {
                'label': 'Profile',
                'name': 'user_profile_tab',
                'url': reverse_lazy('user_profile_tab').replace('/', '#', 1),
                'icon': None,
            },
        ]

        if request.user.is_superuser:
            settings_dropdown_list.append(
                {
                    'label': 'Admin',
                    'name': 'admin_site',
                    'hard_link': True,
                    'url': reverse_lazy('admin:index'),
                    'icon': 'fa-user-md',
                }
            )

        embedded_lib = cp.EMBEDDED_LIB_CORE + [
            'jquery-ui',
            'chart',
            'worldmap',
            'validator',
            'dropzone',
            'datatables',
            'handsontable',
            'pivottable',
        ]

        js_list = [
            'init_sidebar',
            'init_progressbar',
            'init_history_control',
            'init_search_control',
        ]

        return render(request, self.template_name, {
            'focus': side_menu_dict.get('groups')[0].get('values')[0].get('name'),
            # 'focus': 'product_allocation_tab',
            'side_menu_dict': side_menu_dict,
            'settings_dropdown_list': settings_dropdown_list,
            'embedded_lib': embedded_lib,
            'js_list': js_list,
            'searchbar': True,
        })


class SearchResultsViewDefault(DefaultView):
    r"""
    View that loads the search results based on PK and type
    """

    # Overwrite variables
    context_dict = {
        'title': 'Search Page',
        'subtitle': 'Enter a keyword in the top search bar',
        'p': 'You can search for styles, customers, vendors etc.'
    }


class SearchResultsViewOneProduct(ContentView):
    r"""
    View that loads the search results based on PK and type
    """

    # Overwrite method
    def get_context_dict(self, request):

        pk = self.kwargs.get('pk', 0)
        dim_product = get_object_or_404(models.DimProduct, pk=pk)
        dim_product_matches_found = models.FactAllocation.objects.filter(dim_product__id=pk)

        # Find out if product was approved, was-not approved, or did not find a match
        page_reference_color = 'success'
        product_attribute_table = 'product_attribute_table_selected_true'
        is_single_page = True
        if not dim_product_matches_found.exists():
            page_reference_color = 'danger'
            product_attribute_table = 'product_attribute_table_selected_false'

        else:

            # Check if approved
            if not dim_product_matches_found.filter(is_approved=True).first():
                page_reference_color = 'info'
                product_attribute_table = 'product_attribute_table_selected_false'
                is_single_page = False

        # For products that have already been approved or did not find a match
        if is_single_page:

            panel_list = [
                {
                    'row_start': True,
                    'title': 'Cover Sheet',
                    'subtitle': 'approved product',
                    'description': None,
                    'type': 'form_validation',
                    'url': reverse_lazy(product_attribute_table, kwargs={'pk': pk}),
                    'width': 6,
                    'footer': {}
                },
                {
                    'row_end': True,
                    'title': 'Illustrations',
                    'subtitle': 'approved product',
                    'type': 'gallery',
                    'url': reverse_lazy('product_image_gallery', kwargs={'pk': pk}),
                    'width': 6,
                },
                {
                    'full_row': True,
                    'title': 'Measurement Points',
                    'subtitle': 'new product',
                    'type': 'table_read',
                    'url': reverse_lazy('measurement_point_table', kwargs={'pk': dim_product.source_name if not None else 0}),
                    'width': 12,
                },
            ]

        # For products that have to be allocated
        else:

            dim_product_matching = models.FactAllocation.objects.filter(
                dim_product__id=pk,
                is_selected=True
            ).first()
            if dim_product_matching is None:
                dim_product_matching = models.FactAllocation.objects.filter(
                    dim_product__id=pk,
                    priority=1
                ).get()
            dim_product_matching_id = dim_product_matching.dim_product_matching.id

            panel_list = [
                {
                    'full_row': True,
                    'title': 'Recommended Allocation',
                    'subtitle': 'for the new product',
                    'type': 'table',
                    'url': reverse_lazy('allocation_specific_product', kwargs={'pk': pk}),
                    'dependency_list': 'matched_product_illustration matched_product_cover_sheet',
                    'width': 12,
                },
                {
                    'row_start': True,
                    'title': 'Illustrations',
                    'subtitle': 'new product',
                    'type': 'gallery',
                    'url': reverse_lazy('product_image_gallery', kwargs={'pk': pk}),
                    'width': 6,
                },
                {
                    'row_end': True,
                    'name': 'matched_product_illustration',
                    'title': 'Illustrations',
                    'subtitle': 'matched product',
                    'type': 'gallery',
                    'url': reverse_lazy('product_image_gallery'),
                    'url_pk': dim_product_matching_id,
                    'width': 6,
                },
                {
                    'row_start': True,
                    'title': 'Cover Sheet',
                    'subtitle': 'new product',
                    'description': None,
                    'type': 'form_validation',
                    'url': reverse_lazy('product_attribute_table_selected_false', kwargs={'pk': pk}),
                    'width': 6,
                    'footer':
                        {
                            'button_list': [
                                'save'
                            ],
                        }
                },
                {
                    'row_end': True,
                    'name': 'matched_product_cover_sheet',
                    'title': 'Cover Sheet',
                    'subtitle': 'matched product',
                    'description': None,
                    'type': 'form_validation',
                    'url': reverse_lazy('product_attribute_table_selected_true'),
                    'url_pk': dim_product_matching_id,
                    'width': 6,
                    'footer': None
                },
                {
                    'full_row': True,
                    'title': 'Measurement Points',
                    'subtitle': 'new product',
                    'type': 'table_read',
                    'url': reverse_lazy('measurement_point_table', kwargs={'pk': dim_product.source_name if not None else 0}),
                    'width': 12,
                },
            ]

        self.context_dict = {
            'title': 'Search Results',
            'subtitle': 'Product',
            'page_reference': 'Style #: ' + dim_product.style,
            'page_reference_color': page_reference_color,
            'panel_list': panel_list
        }

        return self.context_dict

class SearchResultsViewMultipleProduct(ContentView):
    r"""
    View that loads the search results based on a keyword
    """

    # Overwrite method
    def get_context_dict(self, request):

        keyword = self.kwargs.get('keyword', 0)

        self.context_dict = {
            'title': 'Search Results',
            'subtitle': 'Products',
            'page_reference': 'Keyword: ' + keyword,
            'panel_list': [
                {
                    'full_row': True,
                    'title': 'Findings',
                    'type': 'table_read',
                    'url': reverse_lazy('search_result_product', kwargs={'keyword': keyword}),
                    'width': 12,
                },
            ],
        }

        return self.context_dict


class SearchResultsViewOneSample(ContentView):
    r"""
    View that loads the search results based on PK and type
    """

    # Overwrite method
    def get_context_dict(self, request):

        pk = self.kwargs.get('pk', 0)
        dim = get_object_or_404(models.DimSample, pk=pk)

        self.context_dict = {
            'title': 'Search Results',
            'subtitle': 'Test Report',
            'page_reference': 'File Name: ' + dim.report_file_name,
            'panel_list': [
                {
                    'row_start': True,
                    'title': 'Details',
                    'subtitle': None,
                    'description': None,
                    'type': 'form_validation',
                    'url': reverse_lazy('sample_attribute_table', kwargs={'pk': pk}),
                    'width': 5,
                    'footer': {
                        'button_list': [
                            'save'
                        ],
                    }
                },
                {
                    'title': 'Illustration',
                    'type': 'gallery',
                    'url': reverse_lazy('sample_image_gallery', kwargs={'pk': pk}),
                    'width': 7,
                },
                {
                    'row_end': True,
                    'title': 'Test Results',
                    'type': 'table_read',
                    'url': reverse_lazy('sample_test_report_table', kwargs={'pk': pk}),
                    'width': 7,
                },

            ],
        }

        return self.context_dict


class SearchResultsViewMultipleSample(ContentView):
    r"""
    View that loads the search results based on a keyword
    """

    # Overwrite method
    def get_context_dict(self, request):

        keyword = self.kwargs.get('keyword', 0)

        self.context_dict = {
            'title': 'Search Results',
            'subtitle': 'Test Reports',
            'page_reference': 'Keyword: ' + keyword,
            'panel_list': [
                {
                    'full_row': True,
                    'title': 'Findings',
                    'type': 'table_read',
                    'url': reverse_lazy('search_result_sample', kwargs={'keyword': keyword}),
                    'width': 12,
                },
            ],
        }

        return self.context_dict


class SearchResultsViewOneVendor(ContentView):
    r"""
    View that loads the search results based on PK and type
    """

    # Overwrite method
    def get_context_dict(self, request):

        pk = self.kwargs.get('pk', 0)
        dim_vendor = get_object_or_404(models.DimVendor, pk=pk)

        self.context_dict = {
            'title': 'Search Results',
            'subtitle': 'Vendor',
            'page_reference': 'Vendor Code: ' + dim_vendor.code,
            'panel_list': [
                {
                    'row_start': True,
                    'title': 'Details',
                    'subtitle': None,
                    'description': None,
                    'type': 'form_validation',
                    'url': reverse_lazy('vendor_attribute_table', kwargs={'pk': pk}),
                    'width': 5,
                    'footer': {
                        'button_list': [
                            'save'
                        ],
                    }
                },
                {
                    'row_end': True,
                    'title': 'Location',
                    'subtitle': 'worldmap',
                    'type': 'worldmap',
                    'url': reverse_lazy('vendor_map', kwargs={'pk': pk}),
                    'url_action': reverse_lazy('vendor_map_api', kwargs={'pk': pk}),
                    'width': 7,
                },
                {
                    'full_row': True,
                    'title': 'Sourced Styles',
                    'subtitle': 'in XTS',
                    'type': 'table',
                    'url': reverse_lazy('allocation_confirmed_xts_vendor', kwargs={'pk': pk}),
                    'width': 12,
                },
            ],
        }

        return self.context_dict


class SearchResultsViewMultipleVendor(ContentView):
    r"""
    View that loads the search results based on a keyword
    """

    # Overwrite method
    def get_context_dict(self, request):

        keyword = self.kwargs.get('keyword', 0)

        self.context_dict = {
            'title': 'Search Results',
            'subtitle': 'Vendors',
            'page_reference': 'Keyword: ' + keyword,
            'panel_list': [
                {
                    'full_row': True,
                    'title': 'Findings',
                    'type': 'table_read',
                    'url': reverse_lazy('search_result_vendor', kwargs={'keyword': keyword}),
                    'width': 12,
                },
            ],
        }

        return self.context_dict


class DashboardView(ContentView):
    r"""
    View that loads the Tech-Pack summary dashboard
    """

    # Get numbers from models
    product_style_count = models.DimProduct.objects.count()
    allocated_style_count = models.DimProduct.objects.filter(
        is_approved__exact=True,
    ).count()
    non_allocated_style_count = product_style_count - allocated_style_count
    vendor_count = models.DimVendor.objects.count()
    coo_count = len(set(models.DimVendor.objects.values_list('dim_location', flat=True)))

    # Overwrite variables
    context_dict = {
        'top_tile_list': [
            {
                'width': 2,
                'icon': 'fa-cube',
                'label': 'Total Styles',
                'value': '{:,}'.format(product_style_count),
                'relative_change': {},
            },
            {
                'width': 2,
                'icon': 'fa-check',
                'label': 'Allocated Styles',
                'value': '{:,}'.format(allocated_style_count),
                'relative_change': {},
            },
            {
                'width': 2,
                'icon': 'fa-close',
                'label': 'Non-Allocated Styles',
                'value': '{:,}'.format(non_allocated_style_count),
                'relative_change': {},
            },
            {
                'width': 2,
                'icon': 'fa-building',
                'label': 'Total Vendors',
                'value': vendor_count,
                'relative_change': {},
            },
            {
                'width': 2,
                'icon': 'fa-map-marker',
                'label': 'Total COOs',
                'value': coo_count,
                'relative_change': {},
            },
        ],
        'panel_list': [
            {
                'row_start': True,
                'title': 'Products',
                'subtitle': 'by customer',
                'type': 'bar',
                'url': reverse_lazy('chartjs'),
                'url_action': reverse_lazy('products_by_customer_api'),
                'width': 6,
            },
            {
                'row_end': True,
                'title': 'Allocation Status',
                'subtitle': 'by product type',
                'type': 'bar',
                'url': reverse_lazy('chartjs'),
                'url_action': reverse_lazy('allocation_by_product_type_api'),
                'width': 6,
            },
            # {
            #     'row_start': True,
            #     'title': 'Allocation Status',
            #     'subtitle': 'by gender',
            #     'type': 'bar',
            #     'url': reverse_lazy('chartjs'),
            #     'url_action': reverse_lazy('allocation_by_gender_api'),
            #     'width': 6,
            # },
            # {
            #     'row_end': True,
            #     'title': 'Allocation Recs',
            #     'subtitle': 'by matching priority level',
            #     'type': 'bar',
            #     'url': reverse_lazy('chartjs'),
            #     'url_action': reverse_lazy('allocation_by_priority_api'),
            #     'width': 6,
            # },
            {
                'full_row': True,
                'title': 'Confirmed Allocations',
                'subtitle': 'by COO',
                'type': 'worldmap',
                'url': reverse_lazy('product_allocation_map'),
                'url_action': reverse_lazy('product_allocation_map_api'),
                'width': 12,
            },
            # {
            #     'row_end': True,
            #     'title': 'Vendors',
            #     'subtitle': 'by COO',
            #     'type': 'worldmap',
            #     'url': reverse_lazy('vendor_map'),
            #     'url_action': reverse_lazy('vendor_map_api'),
            #     'width': 6,
            # },
            {
                'row_start': True,
                'title': 'Vendor Allocations',
                'subtitle': 'inside XTS',
                'type': 'table',
                'url': reverse_lazy('allocation_by_vendor_confirmed'),
                'width': 6,
            },
            {
                'row_end': True,
                'title': 'Vendor Allocations',
                'subtitle': 'outside XTS',
                'type': 'table',
                'url': reverse_lazy('allocation_by_vendor_non_confirmed'),
                'width': 6,
            },
        ],
    }



class ProductAllocationView(ContentView):
    r"""
    View that loads the product
    """
    # Overwrite variables
    context_dict = {
        'title': 'Recommended Allocations',
        'subtitle': '',
        'panel_list': [
            {
                'full_row': True,
                'title': 'Decisions to Make',
                'subtitle': None,
                'type': 'table',
                'url': reverse_lazy('allocation_non_confirmed'),
                'width': 12,
            },
        ]
    }


class ProductAllocationViewConfirmed(ContentView):
    r"""
    View that loads the product
    """
    # Overwrite variables
    context_dict = {
        'title': 'Confirmed Allocations',
        'subtitle': 'not in XTS yet',
        'panel_list': [
            {
                'full_row': True,
                'title': 'Decisions Made',
                'subtitle': None,
                'type': 'table',
                'url': reverse_lazy('allocation_confirmed'),
                'width': 12,
            },
        ]
    }


class ProductAllocationViewConfirmedXTS(ContentView):
    r"""
    View that loads the product
    """
    # Overwrite variables
    context_dict = {
        'title': 'Confirmed Allocations',
        'subtitle': 'in XTS',
        'panel_list': [
            {
                'full_row': True,
                'title': 'XTS Orders',
                'subtitle': None,
                'type': 'table',
                'url': reverse_lazy('allocation_confirmed_xts'),
                'width': 12,
            },
        ]
    }


class ImageMatchingView(ContentView):
    r"""
    View that loads the image drag&drop feature
    """
    # Overwrite variables
    context_dict = {
        'title': 'Image Matching',
        'subtitle': 'Operations',
        'panel_list': [
            {
                'full_row': True,
                'name': 'image_upload',
                'title': 'Image Upload',
                'subtitle': 'drag and drop',
                'description': 'Upload images or PDFs containing images.',
                'type': 'upload',
                'url': reverse_lazy('image_matching_view'),
                'url_action': reverse_lazy('image_matching_upload'),
                'dependency_list': 'image_display',
                'width': 7,
            },
            {
                'full_row': True,
                'name': 'image_display',
                'title': 'Image',
                'subtitle': 'display after upload',
                'type': 'gallery',
                'url': reverse_lazy('image_matching_display'),
                'dependency_list': 'image_matching_result',
                'width': 12,
            },
            {
                'full_row': True,
                'name': 'image_matching_result',
                'title': 'Matched Products',
                'subtitle': 'display after upload',
                'type': 'table_read',
                'url': reverse_lazy('image_matching_result_table'),
                'url_pk': '0',
                'width': 12,
            },
        ]
    }


class QCReportView(ContentView):
    r"""
    View that loads the test report summary dashboard
    """

    # Get numbers from models
    sample_count = models.DimSample.objects.count()
    test_passed = models.FactTestReport.objects.filter(
        is_successful=True,
    ).count()
    test_failed = models.FactTestReport.objects.filter(
        is_successful=False,
    ).count()

    # Overwrite variables
    context_dict = {
        'top_tile_list': [
            {
                'width': 2,
                'icon': 'paper-plane-o',
                'label': 'Total Test Reports',
                'value': '{:,}'.format(sample_count),
            },
            {
                'width': 2,
                'icon': 'fa-check',
                'label': 'Passed Tests',
                'value': '{:,}'.format(test_passed),
            },
            {
                'width': 2,
                'icon': 'fa-close',
                'label': 'Failed Tests',
                'value': '{:,}'.format(test_failed),
                'relative_change': {},
            },
        ],
        'panel_list': [
            {
                'full_row': True,
                'title': 'Report Level Analysis (Status)',
                'subtitle': 'Pivot Table',
                'type': 'pivottable',
                'url': reverse_lazy('pivottablejs'),
                'url_action': reverse_lazy('qc_report_pivottable'),
                'pivottable_cols': 'result status',
                'pivottable_rows': 'vendor,label fiber content',
                'pivottable_vals': 'test report count',
                'renderer_name': 'Heatmap',
                'width': 12,
                'overflow': 'auto',
            },
            {
                'full_row': True,
                'title': 'Test Level Analysis (Pass/Fail)',
                'subtitle': 'Pivot Table',
                'type': 'pivottable',
                'url': reverse_lazy('pivottablejs'),
                'url_action': reverse_lazy('pass_fail_report_pivottable'),
                'pivottable_cols': 'successful?',
                'pivottable_rows': 'test',
                'pivottable_vals': 'test count',
                'renderer_name': 'Heatmap',
                'width': 12,
                'overflow': 'auto',
            },
        ],
    }


class MasterTableView(ContentView, mixins_view.SecurityModelNameMixin):
    r"""
    View that loads the master tables for which the user has permissions
    """

    user_permission_model = UserPermissions
    group_permission_model = GroupPermissions
    target_model = Item
    permission_type = 'table'

    def get_context_dict(self, request):
        # Get model name
        model_name = self.get_model_name(request.user)
        model_obj = eval('models.' + model_name)

        # Overwrite last page session variable
        request.session['active_page'] = model_name.lower() + '_tab'

        # Return block
        return {
            'title': 'Master Tables',
            'panel_list': [
                {
                    'full_row': True,
                    'title': model_obj._meta.verbose_name,
                    'type': 'table',
                    'url': reverse_lazy('master_table'),
                    'url_action': reverse_lazy('handsontable', kwargs={'item': model_name}),
                    'url_action_helper': reverse_lazy('handsontable_header', kwargs={'item': model_name}),
                    'width': 12,
                },
            ]
        }


class ProfileView(ContentView):
    r"""
    View that loads the user profile dashboard
    """
    # Overwrite variables
    context_dict = {
        'title': 'Profile',
        'subtitle': 'user details',
        'panel_list': [
            {
                'row_start': True,
                'title': 'Basic Details',
                'subtitle': None,
                'description': None,
                'type': 'form_validation',
                'url': reverse_lazy('user_details'),
                'width': 6,
                'footer':
                    {
                        'button_list': [
                            'save'
                        ],
                    }
            },
            {
                'row_end': True,
                'title': 'Security',
                'subtitle': 'password update',
                'description': None,
                'type': 'form_validation',
                'url': reverse_lazy('user_password'),
                'width': 6,
                'footer':
                    {
                        'button_list': [
                            'save'
                        ],
                    }
            },
        ]
    }
