from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User

from .models import Profile

class UpdateProfile(forms.ModelForm):
    r"""
    Form for User model
    """

    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=False)
    last_name = forms.CharField(required=False)

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name')


class ProfileForm(forms.ModelForm):
    r"""
    Form for Profile model which has a OneToOneField relationship with User model
    """

    location = forms.CharField(required=False, label='Location')
    company = forms.CharField(required=False)
    department = forms.CharField(required=False)
    title = forms.CharField(required=False)

    class Meta:
        model = Profile
        fields = ('location', 'company', 'department', 'title')

    # Cleansing methods
    def clean_location(self):
        value = self.cleaned_data['location']
        if value.lower() == 'china':
            raise ValidationError('Name cannot be ' + value)
        return value
