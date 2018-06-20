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
                        # {
                        #     'name': 'dashboard_tab',
                        #     'label': 'Dashboard',
                        #     'icon': 'fa-dashboard',
                        #     'url': reverse_lazy('dashboard_tab').replace('/', '#', 1),
                        #     'values': None,
                        # },
                        {
                            'name': 'source_tab',
                            'label': 'Source Data',
                            'icon': 'fa-database',
                            'url': reverse_lazy('source_tab').replace('/', '#', 1),
                            'values': None
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
            # {
            #     'label': 'Settings',
            #     'name': 'settings_tab',
            #     'url': reverse_lazy('user_profile_tab').replace('/', '#', 1),
            #     'icon': None,
            # },
            # {
            #     'label': 'Invoices',
            #     'name': 'user_profile_tab',
            #     'url': reverse_lazy('user_profile_tab').replace('/', '#', 1),
            #     'icon': None,
            # },
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


class SourceView(ContentView):
    r"""
    View that loads the core product
    """

    def get_context_dict(self, request):

        # Extend filter
        self.filter_dict = {'user': request.user}

        # Overwrite variables
        return {
            'title': 'Source Extracts',
            'panel_list': [
                {
                    'row_start': True,
                    'title': 'Metadata',
                    'subtitle': 'last modified date',
                    'text': 'Extracted from dedicated folder',
                    'type': 'table',
                    'url': reverse_lazy('metadata_table'),
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
