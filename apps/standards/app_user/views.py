import os

from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.conf import settings as cp
from django.urls import reverse_lazy
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.models import User
from django.forms import inlineformset_factory

from core import utils
from blocks import views
from apps.standards.app_error.forms import PasswordPoliciesChangeCustomizedForm

from .forms import UpdateProfile
from .forms import ProfileForm
from .models import Profile


# class BasicDetails(UpdateView):
#     r"""
#     View that loads the media gallery block
#     """
#     # Define variables
#     template_name = 'blocks/form_validation.html'
#     form_class = ProfileForm
#     model = Profile


class BasicDetails(views.FormValidation):
    r"""
    View that updates user basic details
    """

    template_name = 'blocks/form_validation_dict.html'

    def post_data_processing(self, request):
        user_form = UpdateProfile(request.POST, instance=request.user)
        profile_form = ProfileForm(request.POST, instance=request.user.profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            self.context_dict_additional['message'] = {
                'text': 'Your details were successfully updated!',
                'type': 'success'
            }
        else:
            if not user_form.is_valid():
                self.context_dict_additional['message'] = {
                    'text': user_form.errors,
                    'type': 'danger'
                }
            elif not profile_form.is_valid():
                self.context_dict_additional['message'] = {
                    'text': profile_form.errors,
                    'type': 'danger'
                }

    def get_context_dict(self, request):

        # UserFormSet = inlineformset_factory(User, Profile, fields=('username', 'email', 'location',))
        # formset = UserFormSet(instance=request.user)
        # return {
        #     'form_items': formset
        # }

        return {
            'form_items': [
                {
                    'label': 'Username',
                    'name': 'username',
                    'value': request.user.username,
                    'required': True,
                },
                {
                    'label': 'Email',
                    'name': 'email',
                    'value': request.user.email,
                    'required': True,
                    'type': 'email',
                },
                {
                    'label': 'First Name',
                    'name': 'first_name',
                    'value': request.user.first_name,
                },
                {
                    'label': 'Last Name',
                    'name': 'last_name',
                    'value': request.user.last_name,
                },
                {
                    'label': 'Location',
                    'name': 'location',
                    'value': request.user.profile.location,
                },
                {
                    'label': 'Company',
                    'name': 'company',
                    'value': request.user.profile.company,
                },
                {
                    'label': 'Department',
                    'name': 'department',
                    'value': request.user.profile.department,
                },
                {
                    'label': 'Job Title',
                    'name': 'title',
                    'value': request.user.profile.title,
                },
            ]
        }


class PasswordChange(views.FormValidation):
    r"""
    View that updates the user password
    """

    def get_context_dict(self, request):
        form = PasswordPoliciesChangeCustomizedForm(request.user)
        return {
            'form_items': form
        }

    def post_data_processing(self, request):
        form = PasswordPoliciesChangeCustomizedForm(request.user, request.POST)

        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Update the current session information
            self.context_dict_additional['message'] = {
                'text': 'Your password was successfully updated.',
                'type': 'success',
                'position_left': True,
            }

        self.context_dict_additional['form_items'] = form
