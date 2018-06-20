import os
from datetime import datetime, timedelta

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

from apps.projects.app_dms import models
from apps.projects.app_dms import mixins_view as project_mixins_view


class BaseView(
    project_mixins_view.DMSFilter,
    LoginEnvironmentView,
    mixins_view.SecurityModelNameMixin,
):
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
        self.init_class_dict(request)

        # Get model name list
        self.set_user(request.user)
        model_name_list = self.get_authorized_model_item_list()
        model_name_list = sorted([
            'DimStore',
            'DimChannel',
            'DimLocation',
        ])
        master_table_list = list()
        for model_name in model_name_list:
            model_obj = eval('models.' + model_name)

            master_table_list.append({
                'name': model_name.lower() + '_tab',
                'label': model_obj._meta.verbose_name,
                'url': reverse_lazy('master_table_tab', kwargs={'item': model_name}).replace('/', '#', 1),
            })

        # Prepare wizard dict
        wizard_query = models.DimIAPCycle.objects.filter(**self.filter_dict)
        if wizard_query.filter(is_completed=False).exists():
            wizard_position_current = wizard_query.filter(is_completed=False).order_by('dim_iapstep__position').all().first().dim_iapstep.position
        else:
            wizard_position_current = wizard_query.order_by('dim_iapstep__position').all().last().dim_iapstep.position

        wizard_dict_list = list()
        for step_query in wizard_query.order_by('dim_iapstep__position').all():
            item = wizard_query.filter(dim_iapstep__position=step_query.dim_iapstep.position).get()
            wizard_dict_list.append({
                'label': item.dim_iapstep.name,
                'url_wizard': reverse_lazy('iapcycle_update', kwargs={
                    'dim_iapcycle_id': item.pk,
                    'is_completed': 1 if item.is_completed else 0,
                }),
                'is_completed': item.is_completed,
                'completion_dt': item.completion_dt,
            })

        # Prepare filters
        channel_data_dict = dict()
        for item in models.DimIAPFilter.objects.all().order_by('pk'):
            channel_data_dict[item.dim_channel.id] = item.dim_channel.name

        sales_year_data_dict = dict()
        for item in models.DimIAPFilter.objects.all().order_by('sales_year'):
            sales_year = item.sales_year
            sales_year_data_dict[sales_year] = sales_year
        sales_year_data_dict = {
            '2017': '2017'
        }

        sales_season_data_dict = dict()
        for item in models.DimIAPFilter.objects.all().order_by('sales_season'):
            sales_season = item.sales_season
            sales_season_data_dict[sales_season] = sales_season
        sales_season_data_dict = {
            'SS': 'SS'
        }

        # Prepare template data
        side_menu_dict = {
            'groups':
            [
                {
                    'name': 'General',
                    'values':
                    [
                        {
                            'name': 'strategic_sales_plan_tab',
                            'label': 'Strategic Sales Plan',
                            'icon': 'fa-rocket',
                            'url': reverse_lazy('strategic_sales_plan_tab').replace('/', '#', 1),
                            'values': None,
                        },
                        {
                            'name': 'iap',
                            'label': 'Planning Cycle',
                            'icon': 'fa-pencil',
                            'url': '',
                            'wizard': {
                                'wizard_dict_list': wizard_dict_list,
                                'wizard_position_current': wizard_position_current,
                            },
                            'filter_list': [
                                {
                                    'name': 'dim_channel_id',
                                    'label': 'Channel',
                                    'data': channel_data_dict,
                                    'preselect': self.dim_channel_id
                                },
                                {
                                    'name': 'sales_year',
                                    'label': 'Sales Year',
                                    'data': sales_year_data_dict,
                                    'preselect': self.sales_year
                                },
                                {
                                    'name': 'sales_season',
                                    'label': 'Sales Season',
                                    'data': sales_season_data_dict,
                                    'preselect': self.sales_season
                                },
                            ],
                            'filter_button': {
                                'label': 'Switch',
                                'url': reverse_lazy('iapfilter_update'),
                            },
                            'values':
                            [
                                {
                                    'name': 'store_clustering_tab',
                                    'label': 'Clustering',
                                    # 'url': reverse_lazy('clustering_tab').replace('/', '#', 1),
                                    'sub_values':
                                    [
                                        {
                                            'name': 'clustering_tab_store',
                                            'label': 'Store Clustering',
                                            'url': reverse_lazy('clustering_tab_store').replace('/', '#', 1),
                                        },
                                        {
                                            'name': 'clustering_tab_assortment',
                                            'label': 'Master Assortment',
                                            'url': reverse_lazy('clustering_tab_assortment').replace('/', '#', 1),
                                        },
                                    ]
                                },
                                {
                                    'name': 'sales_planning_tab',
                                    'label': 'Sales Planning',
                                    # 'url': reverse_lazy('sales_planning_tab').replace('/', '#', 1),
                                    'sub_values':
                                    [
                                        {
                                            'name': 'sales_planning_tab_consensus',
                                            'label': 'Consensus Plan',
                                            'url': reverse_lazy('sales_planning_tab_consensus').replace('/', '#', 1),
                                        },
                                        {
                                            'name': 'sales_planning_tab_brand',
                                            'label': 'Brand Plan',
                                            'url': reverse_lazy('sales_planning_tab_brand').replace('/', '#', 1),
                                        },
                                        {
                                            'name': 'sales_planning_tab_retail',
                                            'label': 'Retail Plan',
                                            'url': reverse_lazy('sales_planning_tab_retail').replace('/', '#', 1),
                                        },
                                        {
                                            'name': 'sales_planning_tab_consolidated',
                                            'label': 'Consolidated Plan',
                                            'url': reverse_lazy('sales_planning_tab_consolidated').replace('/', '#', 1),
                                        },
                                    ]
                                },
                                {
                                    'name': 'range_planning_tab',
                                    'label': 'Range Planning',
                                    # 'url': reverse_lazy('range_planning_tab').replace('/', '#', 1),
                                    'sub_values':
                                    [
                                        {
                                            'name': 'range_planning_tab_architecture',
                                            'label': 'Range Architecture',
                                            'url': reverse_lazy('range_planning_tab_architecture').replace('/', '#', 1),
                                        },
                                        {
                                            'name': 'range_planning_tab_master',
                                            'label': 'Range Master',
                                            'url': reverse_lazy('range_planning_tab_master').replace('/', '#', 1),
                                        },
                                    ]
                                },
                                {
                                    'name': 'buy_planning_tab',
                                    'label': 'Buy Planning',
                                    'url': reverse_lazy('buy_planning_tab').replace('/', '#', 1),
                                },
                            ]
                        },
                        {
                            'name': 'summary_tab',
                            'label': 'Dashboard',
                            'icon': 'fa-dashboard',
                            'url': reverse_lazy('summary_tab').replace('/', '#', 1),
                            'values': None
                        },
                        {
                            'name': 'forecast_tab',
                            'label': 'Forecast',
                            'icon': 'fa-line-chart',
                            'url': reverse_lazy('forecast_tab').replace('/', '#', 1),
                            'values': None,
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
                # {
                #     'name': 'Simulations',
                #     'values':
                #     [
                #         {
                #             'name': 'clustering_simulation_tab',
                #             'label': 'Store Clustering',
                #             'icon': 'fa-bar-chart-o',
                #             'url': reverse_lazy('clustering_simulation_tab').replace('/', '#', 1),
                #             'values': None
                #         },
                #
                #     ],
                # }
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
            'datatables',
            'handsontable_pro',
            'pretty_checkbox',
            'daterangepicker',
            'selectpicker',
            # 'pivottable',
        ]

        js_list = [
            'init_sidebar',
            'init_progressbar',
            'init_history_control',
            'init_search_control',
            'init_switchery_control',
        ]

        return render(request, self.template_name, {
            # 'focus': side_menu_dict.get('groups')[0].get('values')[0].get('values')[0].get('name'),
            'focus': 'strategic_sales_plan_tab',
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
        'p': 'You can search for SKU#, styles, stores etc.'
    }


class SearchResultsViewOneProduct(ContentView):
    r"""
    View that loads the search results based on PK and type
    """

    # Overwrite method
    def get_context_dict(self, request):

        # ID
        pk = self.kwargs.get('pk', 0)
        model_obj = get_object_or_404(models.DimProduct, pk=pk)

        self.context_dict = {
            'title': 'Search Results',
            'subtitle': 'Product',
            'page_reference': 'Product Code: ' + model_obj.productcode,
            'panel_list': [
                {
                    'full_row': True,
                    'title': 'Historical Sales',
                    'subtitle': 'units',
                    'type': 'line',
                    'height': 320,
                    'url': reverse_lazy('chartjs'),
                    'url_action': reverse_lazy('historical_sales_chart_api', kwargs={'aggregation': 'units', 'pk': pk, 'category': 'dim_product_id'}),
                    'width': 12,
                },
                {
                    'full_row': True,
                    'title': 'Historical Sales',
                    'subtitle': 'sales value',
                    'type': 'line',
                    'height': 320,
                    'url': reverse_lazy('chartjs'),
                    'url_action': reverse_lazy('historical_sales_chart_api', kwargs={'aggregation': 'salesvalue', 'pk': pk, 'category': 'dim_product_id'}),
                    'width': 12,
                },
                {
                    'row_start': True,
                    'title': 'Attributes',
                    'subtitle': 'description',
                    'description': None,
                    'type': 'form_validation',
                    'url': reverse_lazy('product_attribute_table', kwargs={'pk': pk}),
                    'width': 7,
                    'footer':
                        {
                            'button_list': [
                                'save'
                            ],
                        }
                },
                {
                    'row_end': True,
                    'title': 'Illustration',
                    'subtitle': 'product image',
                    'type': 'image_gallery',
                    'url': reverse_lazy('product_image_gallery', kwargs={'pk': pk}),
                    'width': 5,
                },
            ],
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


class SearchResultsViewOneStore(ContentView):
    r"""
    View that loads the search results based on PK
    """

    # Overwrite method
    def get_context_dict(self, request):

        # ID
        pk = self.kwargs.get('pk', 0)
        model_obj = get_object_or_404(models.DimStore, pk=pk)

        self.context_dict = {
            'title': 'Search Results',
            'subtitle': 'Store',
            'page_reference': 'Store Code: ' + model_obj.store_code,
            'panel_list': [
                {
                    'full_row': True,
                    'title': 'Historical Sales',
                    'subtitle': 'units',
                    'type': 'line',
                    'height': 320,
                    'url': reverse_lazy('chartjs'),
                    'url_action': reverse_lazy('historical_sales_chart_api', kwargs={'aggregation': 'units', 'pk': pk, 'category': 'dim_store_id'}),
                    'width': 12,
                },
                {
                    'full_row': True,
                    'title': 'Historical Sales',
                    'subtitle': 'sales value',
                    'type': 'line',
                    'height': 320,
                    'url': reverse_lazy('chartjs'),
                    'url_action': reverse_lazy('historical_sales_chart_api', kwargs={'aggregation': 'salesvalue', 'pk': pk, 'category': 'dim_store_id'}),
                    'width': 12,
                },
                {
                    'row_start': True,
                    'title': 'Attributes',
                    'subtitle': 'description',
                    'description': None,
                    'type': 'form_validation',
                    'url': reverse_lazy('store_attribute_table', kwargs={'pk': pk}),
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
                    'title': 'Store',
                    'subtitle': 'by country',
                    'type': 'worldmap',
                    'url': reverse_lazy('store_map', kwargs={'pk': pk}),
                    'url_action': reverse_lazy('store_map_api', kwargs={'pk': pk}),
                    'width': 6,
                },
            ],
        }

        return self.context_dict


class SearchResultsViewMultipleStore(ContentView):
    r"""
    View that loads the search results based on a keyword
    """

    # Overwrite method
    def get_context_dict(self, request):

        keyword = self.kwargs.get('keyword', 0)

        self.context_dict = {
            'title': 'Search Results',
            'subtitle': 'Stores',
            'page_reference': 'Keyword: ' + keyword,
            'panel_list': [
                {
                    'full_row': True,
                    'title': 'Findings',
                    'type': 'table_read',
                    'url': reverse_lazy('search_result_store', kwargs={'keyword': keyword}),
                    'width': 12,
                },
            ],
        }

        return self.context_dict


class SummaryView(ContentView):
    r"""
    View that loads the summary dashboard
    """

    def get_context_dict(self, request):

        # Shortcuts
        start_d = 20170101
        filtered_model = models.FactMovements.objects.filter(
            dim_date__id__gte=start_d,
            movementtype='S',
        )

        # Get numbers from models
        store_count = models.DimStore.objects.count()
        store_count_open = models.DimStore.objects.filter(is_active=True).count()
        # store_count_close = models.DimStore.objects.filter(is_active=False).count()
        product_count = models.DimProduct.objects.count()
        # cluster_count = len(set(models.FeatureStoreInput.objects.values_list('cluster_ai', flat=True)))

        sales_unit_sum = filtered_model.aggregate(Sum('units')).get('units__sum')
        sales_value_sum = filtered_model.aggregate(Sum('salesvalue')).get('salesvalue__sum')

        # Overwrite variables
        return {
            'top_tile_list': [
                {
                    'width': 3,
                    'icon': 'fa-shopping-bag',
                    'label': 'Total Stores (active)',
                    'value': '{:,}'.format(store_count_open),
                    'relative_change': {},
                },
                {
                    'width': 3,
                    'icon': 'fa-shopping-cart',
                    'label': 'Total Products',
                    'value': '{:,}'.format(product_count),
                    'relative_change': {},
                },
                {
                    'width': 3,
                    'icon': 'fa-line-chart',
                    'label': 'Units Sold (2017-01 to 2018-01)',
                    'value': '{}'.format(utils.millions_formatter(sales_unit_sum)),
                    'relative_change': {},
                },
                {
                    'width': 3,
                    'icon': 'fa-area-chart',
                    'label': 'Sales Value (2017-01 to 2018-01)',
                    'value': '{}'.format(utils.millions_formatter(sales_value_sum)),
                    'relative_change': {},
                },
            ],
            'panel_list': [
                {
                    'full_row': True,
                    'title': 'Historical Sales',
                    'subtitle': 'units',
                    'type': 'line',
                    'height': 350,
                    'url': reverse_lazy('chartjs'),
                    'url_action': reverse_lazy('historical_sales_chart_api', kwargs={'aggregation': 'units'}),
                    'width': 12,
                },
                {
                    'full_row': True,
                    'title': 'Store',
                    'subtitle': 'by country',
                    'type': 'worldmap',
                    'url': reverse_lazy('store_map'),
                    'url_action': reverse_lazy('store_map_api'),
                    'width': 12,
                },

            ],
        }


class StrategicSalesPlanView(ContentView):
    r"""
    View that loads the range planning
    """
    # Overwrite variables
    context_dict = {
        'title': 'Strategic Sales Plan',
        'panel_list': [
            {
                'full_row': True,
                'title': '3 Year Plan',
                'description': 'Projected values have a <span style="color: rgb(198, 152, 152);">red background</span>.',
                'type': 'table_read',
                'url': reverse_lazy('strategic_sales_plan'),
                'url_pk': 'sales_year',
                'width': 12,
                'overflow': 'auto',
                'footer': {
                    'button_list': [
                        'save'
                    ],
                    'select_name': 'level',
                    'select_values': {
                        'sales_year': 'region',
                        'sales_season': 'season',
                        'dim_channel__name': 'channel',
                    }
                },
            },
            # {
            #     'full_row': True,
            #     'title': 'Range Plan',
            #     'subtitle': 'table',
            #     'type': '',
            #     # 'url': reverse_lazy('measurement_point_table', kwargs={'pk': 1}),
            #     'width': 12,
            # },
        ]
    }


class ClusteringView(ContentView, mixins_view.SecurityModelNameMixin):
    r"""
    View that loads the store clustering
    """

    user_permission_model = UserPermissions
    group_permission_model = GroupPermissions
    target_model = Item
    permission_type = 'table'

    # Overwrite variables
    context_dict = {
        'title': 'Store Clustering',
        'subtitle': 'planning operations',
        'panel_list': [
            {
                'row_start': True,
                'title': 'Clusters',
                'subtitle': 'by AI',
                'type': 'bar',
                'url': reverse_lazy('chartjs'),
                'url_action': reverse_lazy('store_by_cluster_ai_api'),
                'width': 6,
            },
            {
                'row_end': True,
                'title': 'Clusters',
                'subtitle': 'by user',
                'type': 'bar',
                'url': reverse_lazy('chartjs'),
                'url_action': reverse_lazy('store_by_cluster_user_api'),
                'width': 6,
            },
            {
                'full_row': True,
                'title': 'Stores',
                'subtitle': 'by clusters',
                'description': 'Only the field <strong>cluster user</strong> is editable',
                'type': 'table',
                'url': reverse_lazy('master_table'),
                'url_action': reverse_lazy('handsontable', kwargs={'item': 'FeatureStoreInput'}),
                'url_action_helper': reverse_lazy('handsontable_header', kwargs={'item': 'FeatureStoreInput'}),
                'width': 12,
            },
            {
                'full_row': True,
                'title': 'Master Assortment',
                'subtitle': 'by cluster',
                'type': 'table_read',
                'url': reverse_lazy('master_assortment_by_cluster'),
                'width': 12,
            },
        ]
    }


class ClusteringViewStore(ContentView):
    r"""
    View that loads the store clustering
    """

    # Overwrite variables
    context_dict = {
        'title': 'Clustering',
        'subtitle': 'planning operations',
        'panel_list': [
            {
                'row_start': True,
                'title': 'Clusters',
                'subtitle': 'by AI',
                'type': 'bar',
                'url': reverse_lazy('chartjs'),
                'url_action': reverse_lazy('store_by_cluster_ai_api'),
                'width': 6,
            },
            {
                'row_end': True,
                'title': 'Clusters',
                'subtitle': 'by user',
                'type': 'bar',
                'url': reverse_lazy('chartjs'),
                'url_action': reverse_lazy('store_by_cluster_user_api'),
                'width': 6,
            },
            {
                'full_row': True,
                'title': 'Stores',
                'subtitle': 'by clusters',
                'description': 'Only the field <strong>cluster user</strong> is editable',
                'type': 'table',
                'url': reverse_lazy('master_table'),
                'url_action': reverse_lazy('handsontable', kwargs={'item': 'FeatureStoreInput'}),
                'url_action_helper': reverse_lazy('handsontable_header', kwargs={'item': 'FeatureStoreInput'}),
                'width': 12,
            },
        ]
    }


class ClusteringViewAssortment(ContentView):
    r"""
    View that loads the store clustering
    """

    # Overwrite variables
    context_dict = {
        'title': 'Clustering',
        'subtitle': 'planning operations',
        'panel_list': [
            {
                'full_row': True,
                'title': 'Master Assortment',
                'subtitle': 'by cluster',
                'type': 'table_read',
                'url': reverse_lazy('master_assortment_by_cluster'),
                'overflow': 'auto',
                'width': 12,
            },
        ]
    }


class SalesPlanningView(ContentView):
    r"""
    View that loads the sales planning
    """

    # Overwrite variables
    context_dict = {
        'title': 'Sales Planning',
        'subtitle': 'planning operations',
        'panel_list': [
            # {
            #     'row_start': True,
            #     'title': 'Sales Plan Chart',
            #     'subtitle': 'units',
            #     'type': 'line',
            #     'url': reverse_lazy('chartjs'),
            #     'url_action': reverse_lazy('sales_plan_chart_api', kwargs={'aggregation': 'unit'}),
            #     'width': 6,
            # },
            # {
            #     'row_end': True,
            #     'title': 'Sales Plan Chart',
            #     'subtitle': 'sales value',
            #     'type': 'line',
            #     'url': reverse_lazy('chartjs'),
            #     'url_action': reverse_lazy('sales_plan_chart_api', kwargs={'aggregation': 'value'}),
            #     'width': 6,
            # },
            {
                'row_start': True,
                'title': 'Consensus Plan',
                'subtitle': 'by month',
                'type': 'table_read',
                'url': reverse_lazy('sales_plan_by_month'),
                'width': 12,
                # 'footer':
                #     {
                #         'button_list': [
                #             'save',
                #         ],
                #     }
            },
            {
                'row_start': True,
                'title': 'Brand Plan',
                'type': 'table_read',
                'url': reverse_lazy('sales_plan_by_product_category'),
                'url_pk': 'product_category',
                'width': 12,
                'overflow': 'auto',
                'footer': {
                    'button_list': [
                        'save'
                    ],
                    'select_name': 'level',
                    'select_values': {
                        'product_category': 'product category',
                        'product_division': 'product group',
                    }
                },
            },
            {
                'row_end': True,
                'title': 'Retail Plan',
                'type': 'table_read',
                'url': reverse_lazy('sales_plan_by_store'),
                'url_pk': 'store_code',
                'width': 12,
                'overflow': 'auto',
                'footer': {
                    'button_list': [
                        'save'
                    ],
                    'select_name': 'level',
                    'select_values': {
                        'store_code': 'store',
                        'cluster_user': 'cluster',
                    }
                },
            },
            # {
            #     'full_row': True,
            #     'title': 'Consolidated Plan',
            #     'subtitle': 'by plan month, store and brand',
            #     'type': 'table_read',
            #     'url': None,
            #     'width': 12,
            # },
        ]
    }


class SalesPlanningViewConsensus(ContentView, mixins_view.SecurityModelNameMixin):
    r"""
    View that loads the sales planning
    """

    # Overwrite variables
    context_dict = {
        'title': 'Sales Planning',
        'subtitle': 'planning operations',
        'panel_list': [
            {
                'full_row': True,
                'title': 'Consensus Plan',
                'subtitle': 'by month',
                'type': 'table_read',
                'url': reverse_lazy('sales_plan_by_month'),
                'width': 12,
                'footer':
                    {
                        'button_list': [
                            'save',
                        ],
                    }
            },
        ]
    }


class SalesPlanningViewBrand(ContentView, mixins_view.SecurityModelNameMixin):
    r"""
    View that loads the sales planning
    """

    # Overwrite variables
    context_dict = {
        'title': 'Sales Planning',
        'subtitle': 'planning operations',
        'panel_list': [
            {
                'full_row': True,
                'title': 'Brand Plan',
                'type': 'table_read',
                'url': reverse_lazy('sales_plan_by_product_category'),
                'url_pk': 'product_category',
                'width': 12,
                'overflow': 'auto',
                'footer': {
                    'button_list': [
                        'save'
                    ],
                    'select_name': 'level',
                    'select_values': {
                        'product_category': 'product category',
                        'product_division': 'product group',
                    }
                },
            },
        ]
    }


class SalesPlanningViewRetail(ContentView, mixins_view.SecurityModelNameMixin):
    r"""
    View that loads the sales planning
    """

    # Overwrite variables
    context_dict = {
        'title': 'Sales Planning',
        'subtitle': 'planning operations',
        'panel_list': [
            {
                'full_row': True,
                'title': 'Retail Plan',
                'type': 'table_read',
                'url': reverse_lazy('sales_plan_by_store'),
                'url_pk': 'store_code',
                'width': 12,
                'overflow': 'auto',
                'footer': {
                    'button_list': [
                        'save'
                    ],
                    'select_name': 'level',
                    'select_values': {
                        'store_code': 'store',
                        'cluster_user': 'cluster',
                    }
                },
            },
        ]
    }


class SalesPlanningViewConsolidated(ContentView, mixins_view.SecurityModelNameMixin):
    r"""
    View that loads the sales planning
    """

    # Overwrite variables
    context_dict = {
        'title': 'Sales Planning',
        'subtitle': 'planning operations',
        'panel_list': [
            {
                'full_row': True,
                'title': 'Consolidated Plan',
                'subtitle': 'under development',
                # 'subtitle': 'by plan month, store and brand',
                'type': 'table_read',
                'url': None,
                'width': 12,
            },
        ]
    }


class RangePlanningView(ContentView):
    r"""
    View that loads the range planning
    """
    # Overwrite variables
    context_dict = {
        'title': 'Range Planning',
        'panel_list': [
            {
                'full_row': True,
                'title': 'Range Architecture',
                'type': 'table_read',
                'url': reverse_lazy('range_architecture'),
                'width': 12,
                'overflow': 'auto',
                # 'footer': {
                #     'button_list': [
                #         'save'
                #     ],
                # },
            },
            {
                'full_row': True,
                'title': 'Range Master',
                'subtitle': 'from ERP',
                'type': 'table',
                'url': reverse_lazy('master_table'),
                'url_action': reverse_lazy('handsontable', kwargs={'item': 'RangeMaster'}),
                'url_action_helper': reverse_lazy('handsontable_header', kwargs={'item': 'RangeMaster'}),
                'width': 12,
            },
        ]
    }


class RangePlanningViewArchitecture(ContentView):
    r"""
    View that loads the range planning
    """
    # Overwrite variables
    context_dict = {
        'title': 'Range Planning',
        'panel_list': [
            {
                'full_row': True,
                'title': 'Range Architecture',
                'type': 'table_read',
                'url': reverse_lazy('range_architecture'),
                'width': 12,
                'overflow': 'auto',
                'footer': {
                    'button_list': [
                        'save'
                    ],
                },
            },
        ]
    }


class RangePlanningViewMaster(ContentView):
    r"""
    View that loads the range planning
    """
    # Overwrite variables
    context_dict = {
        'title': 'Range Planning',
        'panel_list': [
            {
                'full_row': True,
                'title': 'Range Master',
                'subtitle': 'from ERP',
                'type': 'table',
                'url': reverse_lazy('master_table'),
                'url_action': reverse_lazy('handsontable', kwargs={'item': 'RangeMaster'}),
                'url_action_helper': reverse_lazy('handsontable_header', kwargs={'item': 'RangeMaster'}),
                'width': 12,
            },
        ]
    }


class BuyPlanningView(ContentView):
    r"""
    View that loads the buy planning
    """
    # Overwrite variables
    context_dict = {
        'title': 'Buy Planning',
        'subtitle': 'under development',
        'panel_list': []
    }


class ForecastView(ContentView):
    r"""
    View that loads the sales forecast
    """

    # Overwrite variables
    def __init__(self):
        super(ContentView, self).__init__()
        self.js_list.append('init_daterangepicker_control')
        self.js_list.append('init_selectpicker_control')

    def get_context_dict(self, request):

        # Shortcuts
        # filtered_model = models.FactDemandTotal.objects.filter(**self.filter_dict, **{'dim_demand_category_id__exact': 22})

        country_list_of_dict = list()
        for idx, item in enumerate(sorted(models.DimStore.objects.all().values_list('dim_location__country', flat=True).distinct())):
            temp_dict = {
                'value': item,
                'label': item,
                'selected': False,
            }
            country_list_of_dict.append(temp_dict)

        return {
            'title': 'Forecast',
            'subtitle': 'SARIMA model',
            # 'daterange_start': ((datetime.today().replace(day=1) - timedelta(days=95)).replace(day=1)).strftime('%Y-%m-%d'),
            # 'daterange_end': (datetime.today() + timedelta(days=42)).strftime('%Y-%m-%d'),
            'daterange_start': (datetime(2017, 4, 1)).strftime('%Y-%m-%d'),
            'daterange_end': (datetime.today()).strftime('%Y-%m-%d'),
            'selectpicker': [
                {
                    'name': 'level',
                    'label': 'Level',
                    'type': 'group_by',
                    'live_search': False,
                    'action_box': False,
                    'multiple': False,
                    'values': [
                        {
                            'value': 'dim_date__year_month_name',
                            'label': 'Month',
                            'selected': True,
                        },
                        {
                            'value': 'dim_date__sales_cw',
                            'label': 'Week',
                        },
                    ]
                },
                {
                    'name': 'aggregation',
                    'label': 'Aggregation',
                    'type': 'aggregation',
                    'live_search': False,
                    'action_box': False,
                    'multiple': False,
                    'values': [
                        {
                            'value': 'units',
                            'label': 'Units',
                            'type': 'sum',
                            'selected': True,
                        },
                        {
                            'value': 'salesvalue',
                            'label': 'Sales Value',
                        },
                    ]
                },
                {
                    'name': 'dim_store__dim_location__country',
                    'label': 'Store Country',
                    'type': 'filter',
                    'live_search': True,
                    'action_box': True,
                    'multiple': True,
                    'values': country_list_of_dict,
                },
                {
                    'label': 'Date Range',
                    'type': 'daterangepicker',
                },
                {
                    'name': 'dim_product__style',
                    'label': 'Product Style',
                    'type': 'tokenfield',
                    'url': reverse_lazy('tokenfield_dimproduct_style'),
                },
            ],
            'panel_list': [
                {
                    'full_row': True,
                    'title': 'Sales Units',
                    'subtitle': None,
                    'type': '',
                    'type': 'line',
                    'url': reverse_lazy('chartjs'),
                    'url_action': reverse_lazy('sales_forecast_api'),
                    # 'url_action': reverse_lazy('sales_forecast_api', kwargs={'aggregation': 'units'}),
                    'width': 12,
                    'height': 480,
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


class ClusteringSimulationView(ContentView):
    r"""
    View that loads the clustering simulation for users to play
    """
    # Overwrite variables
    context_dict = {
        'title': 'Store Clustering',
        'subtitle': 'Simulation',
        'panel_list': [
            {
                'full_row': True,
                'title': 'Algorithm Configuration',
                'type': 'selection_filter',
                'url': '',
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
