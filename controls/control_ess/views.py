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

from apps.standards.app_pipeline import models


class BaseView(LoginEnvironmentView, mixins_view.SecurityModelNameMixin):
    r"""
    View that loads the base application structure after user authentication
    """
    # Define variables
    template_name = 'architecture/application_structure.html'

    def get(self, request):

        # Get model name list
        self.set_user(request.user)

        # Prepare template data
        side_menu_dict = {
            'groups':
            [
                {
                    'name': 'General',
                    'values':
                    [
                        {
                            'name': 'source_tab',
                            'label': 'Source Data',
                            'icon': 'fa-database',
                            'url': reverse_lazy('source_tab').replace('/', '#', 1),
                            'values': None
                        },
                        {
                            'name': 'dashboard_tab',
                            'label': 'Visualization',
                            'icon': 'fa-dashboard',
                            'url': reverse_lazy('dashboard_tab').replace('/', '#', 1),
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
            'datatables',
        ]

        js_list = [
            'init_sidebar',
            'init_progressbar',
            'init_history_control',
        ]

        # Check session variable for focus
        return render(request, self.template_name, {
            'focus': 'source_tab',
            'side_menu_dict': side_menu_dict,
            'settings_dropdown_list': settings_dropdown_list,
            'embedded_lib': embedded_lib,
            'js_list': js_list,
            'searchbar': False,
        })


class DashboardView(ContentView):
    r"""
    View that loads the summary dashboard
    """

    def get_context_dict(self, request):

        # Overwrite variables
        return {
            'panel_list': [
                # {
                #     'full_row': True,
                #     'title': 'Production Demand',
                #     'subtitle': self.dim_release_comment,
                #     'type': 'bar',
                #     'height': 320,
                #     'url': reverse_lazy('combochartjs'),
                #     'url_action': reverse_lazy('latest_demand_combochart_api'),
                #     'width': 12,
                # },
                # {
                #     'full_row': True,
                #     'title': 'Scenario Comparison',
                #     'subtitle': 'Pivot Table',
                #     'type': 'pivottable',
                #     'url': reverse_lazy('pivottablejs'),
                #     'url_action': reverse_lazy('scenario_pivottable'),
                #     'pivottable_cols': 'scenario',
                #     'pivottable_rows': 'XF month (user),production line',
                #     'pivottable_vals': 'quantity (user)',
                #     'renderer_name': 'Heatmap',
                #     # 'hide_row_totals': True,
                #     'width': 12,
                #     'overflow': 'auto',
                # },
            ]
        }


class SourceView(ContentView):
    r"""
    View that loads the core product
    """

    def get_context_dict(self, request):

        # Get numbers from models
        text_file_format_count = models.Metadata.objects.filter(extension__in=['txt', 'csv', 'txt', 'dat', 'log', 'json', 'xml', 'html']).count()
        spreadsheet_file_format_count = models.Metadata.objects.filter(extension__in=['xlsx', 'xls', 'pdf', 'ods']).count()
        database_format_count = models.Metadata.objects.filter(extension__in=['sql']).count()

        # Overwrite variables
        return {
            'top_tile_list': [
                {
                    'width': 2,
                    'icon': 'fa-file',
                    'label': 'Text Format Files',
                    'value': '{:,}'.format(text_file_format_count),
                    'relative_change': {},
                },
                {
                    'width': 2,
                    'icon': 'fa-file-excel-o',
                    'label': 'Spreadsheet Format Files',
                    'value': '{:,}'.format(spreadsheet_file_format_count),
                    'relative_change': {},
                },
                {
                    'width': 2,
                    'icon': 'fa-database',
                    'label': 'SQL Integrations',
                    'value': '{:,}'.format(database_format_count),
                    'relative_change': {},
                },
            ],
            'panel_list': [
                {
                    'full_row': True,
                    'title': 'Metadata',
                    'subtitle': 'last modified date',
                    'text': 'Extracted from dedicated folder',
                    'type': 'table',
                    'url': reverse_lazy('metadata_table'),
                    'width': 12,
                },
                {
                    'row_start': True,
                    'title': 'Row Count',
                    'subtitle': 'for each file',
                    'type': 'bar',
                    'url': reverse_lazy('chartjs'),
                    'url_action': reverse_lazy('metadata_row_count'),
                    'width': 6,
                },
                {
                    'row_end': True,
                    'title': 'Column Count',
                    'subtitle': 'for each file',
                    'type': 'bar',
                    'url': reverse_lazy('chartjs'),
                    'url_action': reverse_lazy('metadata_col_count'),
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
                'title': 'Excel Refresh',
                'subtitle': None,
                'description': 'These parameters control the data to be refreshed in the Excel reports',
                'type': 'form_validation',
                'url': reverse_lazy('excel_refresh_configuration'),
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
