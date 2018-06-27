import os

from django.conf import settings as cp
from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User

from . import models


class ProductSelectedFalseForm(forms.ModelForm):
    r"""
    Form for model
    """
    dim_season = forms.ModelChoiceField(queryset=models.DimSeason.objects.all(), label='Season')
    dim_customer = forms.ModelChoiceField(queryset=models.DimCustomer.objects.all(), label='Customer')
    dim_product_gender = forms.ModelChoiceField(queryset=models.DimProductGender.objects.all(), label='Gender')
    # dim_product_size_range = forms.ModelChoiceField(queryset=models.DimProductSizeRange.objects.all(), label='Product Size Range')
    dim_product_type = forms.ModelChoiceField(queryset=models.DimProductType.objects.all(), label='Product Type')
    dim_product_class = forms.ModelChoiceField(queryset=models.DimProductClass.objects.all(), label='Product Class')
    dim_product_subclass = forms.ModelChoiceField(queryset=models.DimProductSubclass.objects.all(), label='Product Subclass')
    dim_fabric = forms.ModelChoiceField(queryset=models.DimFabric.objects.all(), label='Fabric')
    dim_vendor = forms.ModelChoiceField(queryset=models.DimVendor.objects.all(), label='Vendor')

    class Meta:
        model = models.DimProduct
        fields = (
            'style',
            'silhouette',
            'description',
            'fabric_weight',
            'fabric_class',
            'dim_customer',
            # 'dim_product_size_range',
            'dim_product_type',
            'dim_product_class',
            'dim_product_subclass',
            'dim_product_gender',
            # 'dim_product_sizes',
            'dim_fabric',
            'dim_season',
            'dim_vendor',
            'fob',
            'is_selected',
        )


class ProductSelectedTrueForm(forms.ModelForm):
    r"""
    Form for model
    """
    dim_season = forms.ModelChoiceField(queryset=models.DimSeason.objects.all(), label='Season')
    dim_customer = forms.ModelChoiceField(queryset=models.DimCustomer.objects.all(), label='Customer')
    dim_product_gender = forms.ModelChoiceField(queryset=models.DimProductGender.objects.all(), label='Gender')
    # dim_product_size_range = forms.ModelChoiceField(queryset=models.DimProductSizeRange.objects.all(), label='Product Size Range')
    dim_product_type = forms.ModelChoiceField(queryset=models.DimProductType.objects.all(), label='Product Type')
    dim_product_class = forms.ModelChoiceField(queryset=models.DimProductClass.objects.all(), label='Product Class')
    dim_product_subclass = forms.ModelChoiceField(queryset=models.DimProductSubclass.objects.all(), label='Product Subclass')
    dim_fabric = forms.ModelChoiceField(queryset=models.DimFabric.objects.all(), label='Fabric')
    dim_vendor = forms.ModelChoiceField(queryset=models.DimVendor.objects.all(), label='Vendor')

    class Meta:
        model = models.DimProduct
        fields = (
            'style',
            'silhouette',
            'description',
            'fabric_weight',
            'fabric_class',
            'dim_customer',
            # 'dim_product_size_range',
            'dim_product_type',
            'dim_product_class',
            'dim_product_subclass',
            'dim_product_gender',
            # 'dim_product_sizes',
            'dim_fabric',
            'dim_season',
            'dim_vendor',
            'fob',
        )


class VendorForm(forms.ModelForm):
    r"""
    Form for model
    """
    dim_location = forms.ModelChoiceField(queryset=models.DimLocation.objects.all(), label='COO')

    class Meta:
        model = models.DimVendor
        fields = (
            'code',
            'name',
            'dim_location',
            'is_active',
        )


class SampleForm(forms.ModelForm):
    r"""
    Form for model
    """

    class Meta:
        model = models.DimSample
        exclude = ('report_file_name', 'image_relative_path', 'has_style')


class FileUploadForm(forms.Form):
    r"""
    Form for uploading files
    """
    # Keep name to 'file' for Dropzone
    file = forms.FileField(required=True)

    class Meta:
        model = models.UploadFile

    def clean_file(self):
        uploaded_file = self.cleaned_data['file']

        # Check if the file is a valid image
        try:
            img = forms.ImageField()
            img.to_python(uploaded_file)

        # Check if the file is a valid PDF
        except forms.ValidationError:
            extension = os.path.splitext(uploaded_file.name)[1][1:].lower()
            if extension != 'pdf':
                raise forms.ValidationError('Only images and PDF files allowed')

        return uploaded_file
