import json

from django.shortcuts import render
from django.urls import resolve
from django.shortcuts import get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import UpdateView as BaseUpdateView
from django.views.generic import ListView as BaseListView
from django.views import View
from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework import status

from password_policies.models import PasswordChangeRequired


class LoginEnvironmentView(LoginRequiredMixin, View):
    r"""
    GCBV for all classes containing the basic security features
    """
    pk = None
    user = None
    filter_dict = None
    post_filter_dict = None
    context_dict = None
    context_dict_additional = None

    def get_context_dict(self, request):
        kwargs = self.kwargs
        return self.context_dict

    def init_class_dict(self, request):
        # Init context dicts
        if self.context_dict is None:
            self.context_dict = dict()
        if self.context_dict_additional is None:
            self.context_dict_additional = dict()

        # Init filter dicts
        if self.filter_dict is None:
            self.filter_dict = dict()
        if self.post_filter_dict is None:
            self.post_filter_dict = dict()

        # Catch page args if any
        if self.pk is None:
            self.pk = self.kwargs.get('pk', 0)
            self.keyword = self.kwargs.get('keyword', None)

        # Store user
        self.user = request.user

        # Prepare additional filters from mixin
        self.init_class_dict_mixin()

        # Prepare additional variables
        self.prepare_variables()

    def init_class_dict_mixin(self):
        pass

    def prepare_variables(self):
        pass

    def get(self, request):
        content = {'message': '401 no access authorization'}
        return Response(content, status=status.HTTP_401_UNAUTHORIZED)

    def post(self, request):
        content = {'message': '401 no access authorization'}
        return Response(content, status=status.HTTP_401_UNAUTHORIZED)

    def delete(self, request):
        content = {'message': '401 no access authorization'}
        return Response(content, status=status.HTTP_401_UNAUTHORIZED)

    def patch(self, request):
        content = {'message': '401 no access authorization'}
        return Response(content, status=status.HTTP_401_UNAUTHORIZED)

    def put(self, request):
        content = {'message': '401 no access authorization'}
        return Response(content, status=status.HTTP_401_UNAUTHORIZED)

    def head(self, request):
        content = {'message': '401 no access authorization'}
        return Response(content, status=status.HTTP_401_UNAUTHORIZED)

    def options(self, request):
        content = {'message': '401 no access authorization'}
        return Response(content, status=status.HTTP_401_UNAUTHORIZED)

    def trace(self, request):
        content = {'message': '401 no access authorization'}
        return Response(content, status=status.HTTP_401_UNAUTHORIZED)


class ContentView(LoginEnvironmentView):
    r"""
    GCBV for dashboards (which contain panels that have their content loaded separately)
    """
    # Define variables
    template_name = 'containers/content.html'
    js_list = [
        'init_toolbox',
        'init_panel_control',
    ]

    def get(self, request, **kwargs):
        self.init_class_dict(request)

        # Update last page session variable
        request.session['active_page'] = resolve(request.path_info).url_name

        self.context_dict = self.get_context_dict(request)
        return self.display(request)

    def display(self, request):
        return render(request, self.template_name, {
            'content_dict': self.context_dict,
            'js_list': self.js_list,
        })


class DefaultView(LoginEnvironmentView):
    r"""
    GCBV for default page result (e.g. search page without keyword)
    """
    # Define variables
    template_name = 'containers/default.html'

    def get(self, request):
        return self.display(request)

    def display(self, request):
        return render(request, self.template_name, {
            'content_dict': self.context_dict,
        })


class BlockView(LoginEnvironmentView):
    r"""
    GCBV for panel contents (blocks)
    """
    # Define variables
    form_class = None
    model = None
    template_name = ''
    js_list = None

    def get(self, request, **kwargs):
        self.init_class_dict(request)
        self.context_dict = self.get_context_dict(request)
        return self.display(request)

    def post(self, request, **kwargs):
        self.init_class_dict(request)

        self.post_data_processing(request)
        self.context_dict = self.get_context_dict(request)
        self.context_dict.update(self.context_dict_additional)
        return self.display(request)

    def post_data_processing(self, request):
        pass

    def prepare_variables(self):
        pass

    def init_class_dict_mixin(self):
        pass

    def display(self, request):
        return render(request, self.template_name, {
            'context_dict': self.context_dict,
            'js_list': self.js_list,
        })


class SimpleView(LoginEnvironmentView):
    r"""
    GCBV for simple operations (CRUD)
    """
    # Define variables
    model = None
    pk = None

    def get(self, request, **kwargs):
        pass


class RPCView(LoginEnvironmentView):
    r"""
    GCBV for controlling remote procedure calls (RPCs)
    """

    def launch_rpc(self):
        return True

    def get(self, request, **kwargs):
        return JsonResponse(self.launch_rpc, safe=False)


class ExtendedListView(BaseListView, LoginEnvironmentView):
    r"""
    GCBV for listing a Django model entry
    """
    context_object_name = 'context_dict'


# class UpdateView(LoginEnvironmentView, BaseUpdateView):
#     r"""
#     GCBV for updating a Django model entry
#     """
#     context_object_name = 'context_dict'
