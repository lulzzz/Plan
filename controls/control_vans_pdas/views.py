import os

from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.conf import settings as cp
from django.urls import reverse_lazy
from django.db.models import Sum

from core.gcbvs import LoginEnvironmentView
from core.gcbvs import ContentView
from core.gcbvs import DefaultView
from core import utils
from core import mixins_view

from apps.standards.app_console.models import UserPermissions
from apps.standards.app_console.models import GroupPermissions
from apps.standards.app_console.models import Item

from apps.projects.app_pdas import models
from apps.projects.app_pdas import mixins_view as project_mixins_view


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
                'name': model_name.lower() + '_tab',
                'label': model_obj._meta.verbose_name,
                'url': reverse_lazy('master_table_tab', kwargs={'item': model_name}).replace('/', '#', 1),
            })

        # Prepare template data
        side_menu_dict = {
            'groups':
            [
                {
                    'name': 'General',
                    'values':
                    [
                        {
                            'name': 'source_data_tab',
                            'label': 'Source Data Analysis',
                            'icon': 'fa-file-excel-o',
                            'url': reverse_lazy('source_data_tab').replace('/', '#', 1),
                            'values': None
                        },
                        {
                            'name': 'procedure_tab',
                            'label': 'System Run',
                            'icon': 'fa-rocket',
                            'url': reverse_lazy('procedure_tab').replace('/', '#', 1),
                            'values': None
                        },
                        {
                            'name': 'dashboard_tab',
                            'label': 'Dashboard',
                            'icon': 'fa-dashboard',
                            'url': reverse_lazy('dashboard_tab').replace('/', '#', 1),
                            'values': None,
                        },
                        {
                            'name': 'report_tab',
                            'label': 'Reports',
                            'icon': 'fa-filter',
                            'url': '',
                            'values': [
                                {
                                    'name': 'report01_tab',
                                    'label': 'Monthly Buy by Region',
                                    'url': reverse_lazy('report01_tab').replace('/', '#', 1),
                                },
                                # {
                                #     'name': 'report02_tab',
                                #     'label': 'Shipment Status by Vendor',
                                #     'url': reverse_lazy('report02_tab').replace('/', '#', 1),
                                # },
                                # {
                                #     'name': 'report03_tab',
                                #     'label': 'Shipment Status by Region',
                                #     'url': reverse_lazy('report03_tab').replace('/', '#', 1),
                                # },
                            ]
                        },
                        {
                            'name': 'master_table',
                            'label': 'Master Tables',
                            'icon': 'fa-table',
                            'url': '',
                            'values': master_table_list
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
            ]
        }

        settings_dropdown_list = [
            {
                'label': 'Profile',
                'name': 'user_profile_tab',
                'url': reverse_lazy('user_profile_tab').replace('/', '#', 1),
                'icon': None,
            },
        ]

        # Add link to admin interface
        if request.user.is_superuser:
            settings_dropdown_list.append(
                {
                    'label': 'Admin',
                    'name': 'admin_site',
                    'url': reverse_lazy('admin:index'),
                    'icon': 'fa-user-md',
                }
            )

        embedded_lib = cp.EMBEDDED_LIB_CORE + [
            'jquery-ui',
            'chart',
            'worldmap',
            'validator',
            'datatables',
            'handsontable',
            'selectpicker',
            'pivottable',
        ]

        js_list = [
            'init_sidebar',
            'init_progressbar',
            'init_history_control',
            'init_search_control',
        ]

        # Check session variable for focus
        return render(request, self.template_name, {
            'focus': 'source_data_tab',
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
        'p': 'You can search for styles, customers, factories etc.'
    }


class SearchResultsViewOneProduct(ContentView):
    r"""
    View that loads the search results based on PK
    """

    # Overwrite method
    def get_context_dict(self, request):

        pk = self.kwargs.get('pk', 0)
        dim_product = get_object_or_404(models.DimProduct, pk=pk)

        panel_list = [
            {
                'full_row': True,
                'title': 'Production Demand',
                'subtitle': 'pairs',
                'type': 'bar',
                'height': 320,
                'url': reverse_lazy('chartjs'),
                'url_action': reverse_lazy('demand_chart_api', kwargs={'aggregation': 'quantity_lum', 'pk': pk, 'category': 'dim_product'}),
                'width': 12,
            },
            {
                'row_start': True,
                'title': 'Attributes',
                'subtitle': None,
                'description': None,
                'type': 'form_validation',
                'url': reverse_lazy('product_attribute_table', kwargs={'pk': pk}),
                'width': 6,
                'footer':
                    {
                        'button_list': [
                            'save'
                        ],
                    }
            },
            # {
            #     'row_start': True,
            #     'title': 'Illustrations',
            #     'subtitle': None,
            #     'type': 'gallery',
            #     'url': reverse_lazy('product_image_gallery', kwargs={'pk': pk}),
            #     'width': 6,
            # },
        ]

        self.context_dict = {
            'title': 'Search Results',
            'subtitle': 'Product',
            'page_reference': 'Ref: ' + dim_product.material_id + ' - ' + dim_product.size,
            'page_reference_color': None,
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
                    'title': 'Production Demand',
                    'subtitle': 'pairs',
                    'type': 'bar',
                    'height': 320,
                    'url': reverse_lazy('chartjs'),
                    'url_action': reverse_lazy('demand_chart_api', kwargs={'aggregation': 'quantity_lum', 'keyword': keyword, 'category': 'dim_product'}),
                    'width': 12,
                },
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


class SearchResultsViewOneVendor(ContentView):
    r"""
    View that loads the search results based on PK and type
    """

    # Overwrite method
    def get_context_dict(self, request):

        pk = self.kwargs.get('pk', 0)
        dim_factory = get_object_or_404(models.DimFactory, pk=pk)

        self.context_dict = {
            'title': 'Search Results',
            'subtitle': 'Vendor',
            'page_reference': 'Factory Code: ' + dim_factory.short_name,
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


class DashboardView(project_mixins_view.ReleaseFilter, ContentView):
    r"""
    View that loads the summary dashboard
    """

    def get_context_dict(self, request):

        # Extend filter
        self.filter_dict['dim_date_id__gte'] = self.dim_release_dim_date_id

        # Get numbers from models
        filtered_model = models.FactDemandTotal.objects.filter(**self.filter_dict)
        product_count = filtered_model.values('dim_product__material_id').distinct().count()
        ntb_volume = filtered_model.aggregate(Sum('quantity_lum')).get('quantity_lum__sum')
        factory_count = filtered_model.values('dim_factory').distinct().count()
        vendor_count = filtered_model.values('dim_factory__vendor_group').distinct().count()

        # Overwrite variables
        return {
            'top_tile_list': [
                {
                    'width': 2,
                    'icon': 'fa-cube',
                    'label': 'MTL Count (active)',
                    'value': '{:,}'.format(product_count),
                    'relative_change': {},
                },
                {
                    'width': 2,
                    'icon': 'fa-shopping-cart',
                    'label': 'Buy Volume',
                    'value': 0 if ntb_volume is None else utils.millions_formatter(ntb_volume),
                    'relative_change': {},
                },
                {
                    'width': 2,
                    'icon': 'fa-building',
                    'label': 'Factory Count (active)',
                    'value': '{:,}'.format(factory_count),
                    'relative_change': {},
                },
                {
                    'width': 2,
                    'icon': 'fa-building',
                    'label': 'Vendor Count (active)',
                    'value': '{:,}'.format(vendor_count),
                    'relative_change': {},
                },
            ],
            'panel_list': [
                {
                    'full_row': True,
                    'title': 'Production Demand',
                    'subtitle': self.dim_release_comment,
                    'type': 'bar',
                    'height': 320,
                    'url': reverse_lazy('chartjs'),
                    'url_action': reverse_lazy('latest_buy_demand_chart_api'),
                    'width': 12,
                },
                {
                    'row_start': True,
                    'title': 'Allocation VFA',
                    'subtitle': 'by factory',
                    'type': 'table_read',
                    'url': reverse_lazy('vfa_allocation_by_vendor_need_to_buy'),
                    'width': 6,
                },
                {
                    'row_end': True,
                    'title': 'Allocation VFA',
                    'subtitle': 'by COO',
                    'type': 'worldmap',
                    'url': reverse_lazy('vfa_allocation_map'),
                    'url_action': reverse_lazy('vfa_allocation_map_api'),
                    'width': 6,
                },
            ]
        }


class Report01View(project_mixins_view.ReleaseFilter, ContentView):
    r"""
    View that loads a report with filters
    """

    # Overwrite variables
    def __init__(self):
        super().__init__()
        self.js_list.append('init_selectpicker_control')

    def get_context_dict(self, request):

        # Shortcuts
        filtered_model = models.FactDemandTotal.objects.filter(**{'dim_demand_category_id__exact': 22})

        release_list_of_dict = list()
        for idx, item in enumerate(sorted(models.DimRelease.objects.all().values_list('comment', flat=True).distinct())):
            temp_dict = {
                'value': item,
                'label': item,
                'selected': True,
            }
            release_list_of_dict.append(temp_dict)

        vendor_list_of_dict = list()
        for idx, item in enumerate(sorted(filtered_model.values_list('dim_factory__short_name', flat=True).distinct())):
            temp_dict = {
                'value': item,
                'label': item,
                'selected': True,
            }
            vendor_list_of_dict.append(temp_dict)

        year_month_list_of_dict = list()
        for idx, item in enumerate(sorted(filtered_model.values_list('dim_date_id_buy_month__year_month_accounting', flat=True).distinct())):
            temp_dict = {
                'value': item,
                'label': item,
                'selected': True,
            }
            year_month_list_of_dict.append(temp_dict)

        # Overwrite variables
        return {
            'title': 'Monthly Buy',
            'subtitle': 'by Region',
            'selectpicker': [
                {
                    'name': 'dim_product__material_id',
                    'label': 'MTL #',
                    'type': 'tokenfield',
                    'url': reverse_lazy('tokenfield_dimproduct_material_id'),
                },
                {
                    'name': 'dim_release__comment',
                    'label': 'Release',
                    'multiple': True,
                    'live_search': True,
                    'action_box': True,
                    'values': release_list_of_dict
                },
                {
                    'name': 'dim_factory__short_name',
                    'label': 'Vendor',
                    'live_search': True,
                    'action_box': True,
                    'multiple': True,
                    'values': vendor_list_of_dict,
                },
            ],
            'panel_list': [
                {
                    'full_row': True,
                    'title': 'View 1',
                    'subtitle': 'summary',
                    'type': 'table_read',
                    'url': reverse_lazy('monthly_buy_by_region'),
                    'width': 12,
                },
                {
                    'full_row': True,
                    'title': 'View 2',
                    'subtitle': 'details',
                    'type': 'pivottable',
                    'url': reverse_lazy('pivottablejs'),
                    'url_action': reverse_lazy('monthly_buy_pivottable'),
                    'pivottable_cols': 'CRD month',
                    'pivottable_rows': 'style complexity,gender,description,color,MTL #,region,demand signal type',
                    'pivottable_vals': 'quantity LUM',
                    'width': 12,
                    'overflow': 'auto',
                },
            ]
        }


class Report02View(project_mixins_view.ReleaseFilter, ContentView):
    r"""
    View that loads a report with filters
    """

    # Overwrite variables
    def __init__(self):
        super().__init__()
        self.js_list.append('init_selectpicker_control')

    def get_context_dict(self, request):

        # Shortcuts
        filtered_model = models.FactDemandTotal.objects.filter(**self.filter_dict, **{'dim_demand_category_id__in': [23, 26]})

        demand_category_list_of_dict = list()
        for idx, item in enumerate(sorted(models.DimDemandCategory.objects.all().values_list('name', flat=True).distinct())):
            temp_dict = {
                'value': item,
                'label': item,
                'selected': True,
            }
            demand_category_list_of_dict.append(temp_dict)

        release_list_of_dict = list()
        for idx, item in enumerate(sorted(models.DimBuyingProgram.objects.all().values_list('name', flat=True).distinct())):
            temp_dict = {
                'value': item,
                'label': item,
                'selected': True,
            }
            release_list_of_dict.append(temp_dict)

        vendor_list_of_dict = list()
        for idx, item in enumerate(sorted(filtered_model.values_list('dim_factory__short_name', flat=True).distinct())):
            temp_dict = {
                'value': item,
                'label': item,
                'selected': True,
            }
            vendor_list_of_dict.append(temp_dict)

        year_month_list_of_dict = list()
        for idx, item in enumerate(sorted(filtered_model.values_list('dim_date__year_month_accounting', flat=True).distinct())):
            temp_dict = {
                'value': item,
                'label': item,
                'selected': True,
            }
            year_month_list_of_dict.append(temp_dict)

        # Overwrite variables
        return {
            'title': 'Shipment Status',
            'subtitle': 'by Vendor',
            'selectpicker': [
                {
                    'name': 'dim_product__material_id',
                    'label': 'MTL #',
                    'type': 'tokenfield',
                    'url': reverse_lazy('tokenfield_dimproduct_material_id'),
                },
                {
                    'name': 'dim_product__material_id_emea',
                    'label': 'MTL # (EMEA)',
                    'type': 'tokenfield',
                    'url': reverse_lazy('tokenfield_dimproduct_material_id_emea'),
                },
                {
                    'name': 'order_number',
                    'label': 'PO #',
                    'type': 'tokenfield',
                    'url': reverse_lazy('tokenfield_order_number'),
                },
                {
                    'name': 'dim_date__year_month_accounting',
                    'label': 'CRD Year-Month',
                    'live_search': True,
                    'action_box': True,
                    'multiple': True,
                    'values': year_month_list_of_dict,
                },
                {
                    'name': 'dim_demand_category__name',
                    'label': 'Demand Signal Type',
                    'multiple': True,
                    'live_search': True,
                    'action_box': True,
                    'values': demand_category_list_of_dict
                },
                {
                    'name': 'dim_buying_program__name',
                    'label': 'Buying Program',
                    'multiple': True,
                    'live_search': True,
                    'action_box': True,
                    'values': release_list_of_dict
                },
                {
                    'name': 'dim_factory__short_name',
                    'label': 'Vendor',
                    'live_search': True,
                    'action_box': True,
                    'multiple': True,
                    'values': vendor_list_of_dict,
                },
            ],
            'panel_list': [
                {
                    'full_row': True,
                    'title': 'View 1',
                    'subtitle': 'summary',
                    'type': 'pivottable',
                    'url': reverse_lazy('pivottablejs'),
                    'url_action': reverse_lazy('shipment_status_vendor_pivottable'),
                    'pivottable_cols': 'demand signal type,CRD month',
                    'pivottable_rows': 'vendor',
                    'pivottable_vals': 'quantity LUM',
                    'width': 12,
                    'overflow': 'auto',
                },
                {
                    'full_row': True,
                    'title': 'View 2',
                    'subtitle': 'details',
                    'type': 'pivottable',
                    'url': reverse_lazy('pivottablejs'),
                    'url_action': reverse_lazy('shipment_status_vendor_pivottable'),
                    'pivottable_cols': 'demand signal type,CRD month',
                    'pivottable_rows': 'style complexity,gender,description,color,MTL #,MTL # (EMEA),vendor',
                    'pivottable_vals': 'quantity LUM',
                    'width': 12,
                    'overflow': 'auto',
                },
            ]
        }


class Report03View(project_mixins_view.ReleaseFilter, ContentView):
    r"""
    View that loads a report with filters
    """

    # Overwrite variables
    def __init__(self):
        super().__init__()
        self.js_list.append('init_selectpicker_control')

    def get_context_dict(self, request):

        # Shortcuts
        filtered_model = models.FactDemandTotal.objects.filter(**self.filter_dict, **{'dim_demand_category_id__in': [23, 26]})

        demand_category_list_of_dict = list()
        for idx, item in enumerate(sorted(models.DimDemandCategory.objects.all().values_list('name', flat=True).distinct())):
            temp_dict = {
                'value': item,
                'label': item,
                'selected': True if item in ['Open Order', 'Shipped Order'] else False,
            }
            demand_category_list_of_dict.append(temp_dict)

        release_list_of_dict = list()
        for idx, item in enumerate(sorted(models.DimBuyingProgram.objects.all().values_list('name', flat=True).distinct())):
            temp_dict = {
                'value': item,
                'label': item,
                'selected': True,
            }
            release_list_of_dict.append(temp_dict)

        region_list_of_dict = list()
        for idx, item in enumerate(sorted(models.DimLocation.objects.all().values_list('region', flat=True).distinct())):
            temp_dict = {
                'value': item,
                'label': item,
                'selected': True,
            }
            region_list_of_dict.append(temp_dict)

        year_month_list_of_dict = list()
        for idx, item in enumerate(sorted(filtered_model.values_list('dim_date__year_month_accounting', flat=True).distinct())):
            temp_dict = {
                'value': item,
                'label': item,
                'selected': True,
            }
            year_month_list_of_dict.append(temp_dict)

        # Overwrite variables
        return {
            'title': 'Shipment Status',
            'subtitle': 'by Region',
            'selectpicker': [
                {
                    'name': 'dim_product__material_id',
                    'label': 'MTL #',
                    'type': 'tokenfield',
                    'url': reverse_lazy('tokenfield_dimproduct_material_id'),
                },
                {
                    'name': 'dim_product__material_id_emea',
                    'label': 'MTL # (EMEA)',
                    'type': 'tokenfield',
                    'url': reverse_lazy('tokenfield_dimproduct_material_id_emea'),
                },
                {
                    'name': 'order_number',
                    'label': 'PO #',
                    'type': 'tokenfield',
                    'url': reverse_lazy('tokenfield_order_number'),
                },
                {
                    'name': 'dim_date__year_month_accounting',
                    'label': 'CRD Year-Month',
                    'live_search': True,
                    'action_box': True,
                    'multiple': True,
                    'values': year_month_list_of_dict,
                },
                {
                    'name': 'dim_demand_category__name',
                    'label': 'Demand Signal Type',
                    'multiple': True,
                    'values': demand_category_list_of_dict
                },
                {
                    'name': 'dim_buying_program__name',
                    'label': 'Buying Program',
                    'multiple': True,
                    'values': release_list_of_dict
                },
                {
                    'name': 'dim_customer__dim_location__region',
                    'label': 'Region',
                    'live_search': True,
                    'action_box': True,
                    'multiple': True,
                    'values': region_list_of_dict,
                },
            ],
            'panel_list': [
                {
                    'full_row': True,
                    'title': 'View 1',
                    'subtitle': 'summary',
                    'type': 'pivottable',
                    'url': reverse_lazy('pivottablejs'),
                    'url_action': reverse_lazy('shipment_status_region_pivottable'),
                    'pivottable_cols': 'vendor',
                    'pivottable_rows': 'demand signal type,region',
                    'pivottable_vals': 'quantity LUM',
                    'width': 12,
                    'overflow': 'auto',
                },
                {
                    'full_row': True,
                    'title': 'View 2',
                    'subtitle': 'details',
                    'type': 'pivottable',
                    'url': reverse_lazy('pivottablejs'),
                    'url_action': reverse_lazy('shipment_status_region_pivottable'),
                    'pivottable_cols': 'vendor',
                    'pivottable_rows': 'style complexity,gender,description,color,MTL #,MTL # (EMEA),demand signal type,region',
                    'pivottable_vals': 'quantity LUM',
                    'width': 12,
                    'overflow': 'auto',
                },
            ]
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


class ProcedureView(ContentView):
    r"""
    View that loads the stored procedures for the system run
    """

    # Overwrite variables
    context_dict = {
        'title': 'System Run',
        'panel_list': [
            {
                'row_start': True,
                'title': 'Procedures',
                'subtitle': 'PDAS steps',
                'type': 'procedure',
                'url': reverse_lazy('procedure_list'),
                'width': 8,
            },
            {
                'row_end': True,
                'title': 'Current Release',
                'type': 'table',
                'url': reverse_lazy('configuration_table'),
                'width': 4,
                'footer':
                    {
                        'button_list': [
                            'save'
                        ],
                    }
            },
        ]
    }


class SourceDataView(project_mixins_view.ReleaseFilter, ContentView):
    r"""
    View that loads the source data analysis reports
    """

    # Overwrite variables
    def get_context_dict(self, request):
        return {
            'title': self.dim_release_comment,
            'panel_list': [
                {
                    'row_start': True,
                    'title': 'Source Extracts',
                    'subtitle': 'last modified date',
                    'text': 'Extracted from ETL shared drive',
                    'type': 'table',
                    'url': reverse_lazy('pdas_metadata_table'),
                    'width': 6,
                },
                {
                    'row_end': True,
                    'title': 'Validation report',
                    'type': 'table',
                    'url': reverse_lazy('validation_table'),
                    'width': 6,
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
