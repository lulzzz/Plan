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

from apps.projects.app_dpp import models
from apps.projects.app_dpp import mixins_view as project_mixins_view


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
                        # {
                        #     'name': 'source_data_tab',
                        #     'label': 'Source Data Analysis',
                        #     'icon': 'fa-file-excel-o',
                        #     'url': reverse_lazy('source_data_tab').replace('/', '#', 1),
                        #     'values': None
                        # },
                        {
                            'name': 'dashboard_tab',
                            'label': 'Dashboard',
                            'icon': 'fa-dashboard',
                            'url': reverse_lazy('dashboard_tab').replace('/', '#', 1),
                            'values': None,
                        },
                        {
                            'name': 'procedure_tab',
                            'label': 'Plan Runs',
                            'icon': 'fa-rocket',
                            'url': reverse_lazy('procedure_tab').replace('/', '#', 1),
                            'values': None
                        },
                        # {
                        #     'name': 'report_tab',
                        #     'label': 'Reports',
                        #     'icon': 'fa-filter',
                        #     'url': reverse_lazy('report01_tab').replace('/', '#', 1),
                        #     'values': None
                        # },
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
            {
                'label': 'Settings',
                'name': 'settings_tab',
                'url': reverse_lazy('settings_tab').replace('/', '#', 1),
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
            'c3',
            'worldmap',
            'validator',
            'datatables',
            'handsontable_pro',
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
            'focus': 'dashboard_tab',
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
            # {
            #     'full_row': True,
            #     'title': 'Production Demand',
            #     'subtitle': 'pairs',
            #     'type': 'bar',
            #     'height': 320,
            #     'url': reverse_lazy('chartjs'),
            #     'url_action': reverse_lazy('demand_chart_api', kwargs={'aggregation': 'quantity_lum', 'pk': pk, 'category': 'dim_product'}),
            #     'width': 12,
            # },
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
            {
                'row_end': True,
                'title': 'Illustrations',
                'subtitle': None,
                'type': 'gallery',
                'url': reverse_lazy('product_image_gallery', kwargs={'pk': pk}),
                'width': 6,
            },
        ]

        self.context_dict = {
            'title': 'Search Results',
            'subtitle': 'Product',
            'page_reference': 'Ref: ' + dim_product.sku,
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
                # {
                #     'full_row': True,
                #     'title': 'Production Demand',
                #     'subtitle': 'pairs',
                #     'type': 'bar',
                #     'height': 320,
                #     'url': reverse_lazy('chartjs'),
                #     'url_action': reverse_lazy('demand_chart_api', kwargs={'aggregation': 'quantity_lum', 'keyword': keyword, 'category': 'dim_product'}),
                #     'width': 12,
                # },
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
            'page_reference': 'Plant Code: ' + dim_factory.plant_code,
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
        self.filter_dict = dict()

        # Get numbers from models
        filtered_model = models.FactDemand.objects.filter(**self.filter_dict)
        product_count = models.DimProduct.objects.count()
        factory_count = models.DimFactory.objects.count()
        production_line_count = models.DimProductionLine.objects.count()

        # Overwrite variables
        return {
            'top_tile_list': [
                {
                    'width': 2,
                    'icon': 'fa-cube',
                    'label': 'Materials',
                    'value': '{:,}'.format(product_count),
                    'relative_change': {},
                },
                {
                    'width': 2,
                    'icon': 'fa-building',
                    'label': 'Plans',
                    'value': '{:,}'.format(factory_count),
                    'relative_change': {},
                },
                {
                    'width': 2,
                    'icon': 'fa-building',
                    'label': 'Production Lines',
                    'value': '{:,}'.format(production_line_count),
                    'relative_change': {},
                },
            ],
            'panel_list': [
                {
                    'full_row': True,
                    'title': 'Scenario Comparison',
                    'subtitle': 'Pivot Table',
                    'type': 'pivottable',
                    'url': reverse_lazy('pivottablejs'),
                    'url_action': reverse_lazy('scenario_pivottable'),
                    'pivottable_cols': 'scenario',
                    'pivottable_rows': 'XF month (user),production line',
                    'pivottable_vals': 'quantity (user)',
                    'renderer_name': 'Heatmap',
                    # 'hide_row_totals': True,
                    'width': 12,
                    'overflow': 'auto',
                },
            ]
        }


class Report01View(ContentView):
    r"""
    View that loads a report with filters
    """

    # Overwrite variables
    def __init__(self):
        super().__init__()
        self.js_list.append('init_selectpicker_control')

    def get_context_dict(self, request):

        # Shortcuts
        filtered_model = models.FactDemand.objects.filter(**self.filter_dict, **{'dim_demand_category_id__exact': 22})

        buying_program_list_of_dict = list()
        for idx, item in enumerate(sorted(models.DimBuyingProgram.objects.all().values_list('name', flat=True).distinct())):
            temp_dict = {
                'value': item,
                'label': item,
                'selected': True,
            }
            buying_program_list_of_dict.append(temp_dict)

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
                    'name': 'dim_date_id_buy_month__year_month_accounting',
                    'label': 'Buy Year-Month',
                    'live_search': True,
                    'action_box': True,
                    'multiple': True,
                    'values': year_month_list_of_dict,
                },
                {
                    'name': 'dim_buying_program__name',
                    'label': 'Buying Program',
                    'multiple': True,
                    'values': buying_program_list_of_dict
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


class ProcedureView(project_mixins_view.ReleaseFilter, ContentView):
    r"""
    View that loads the stored procedures for the system run
    """

    def get_context_dict(self, request):

        # Overwrite variables
        return {
            'title': 'Plan Runs',
            'panel_list': [
                {
                    'row_start': True,
                    'title': 'Procedures',
                    'type': 'procedure',
                    'url': reverse_lazy('procedure_list'),
                    'width': 7,
                },
                {
                    'row_end': True,
                    'title': 'Current Plan',
                    'type': 'table',
                    'url': reverse_lazy('configuration_table'),
                    'width': 5,
                    'footer':
                        {
                            'button_list': [
                                'save'
                            ],
                        }
                },
                {
                    'full_row': True,
                    'title': 'Production Demand',
                    'subtitle': self.dim_release_comment,
                    'type': 'bar',
                    'height': 320,
                    'url': reverse_lazy('combochartjs'),
                    'url_action': reverse_lazy('latest_demand_combochart_api'),
                    'width': 12,
                },
            ]
        }



class SourceDataView(ContentView):
    r"""
    View that loads the source data analysis reports
    """

    # Overwrite variables
    context_dict = {
        'title': 'Source Data Analysis',
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


class SettingsView(ContentView):
    r"""
    View that loads the settings
    """
    # Overwrite variables
    context_dict = {
        'title': 'Settings',
        'panel_list': [
            {
                'full_row': True,
                'title': 'Scenario Configuration',
                # 'description': '',
                'type': 'tree',
                'url': reverse_lazy('scenario_configuration'),
                'width': 12,
                'footer':
                    {
                        'button_list': [
                            'save'
                        ],
                    }
            },
        ]
    }
