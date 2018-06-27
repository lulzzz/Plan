from rest_framework import serializers

from core import utils

from . import models
from . import mixins_serializer

class DimLocationSerializer(
    mixins_serializer.RegionLookup,
    mixins_serializer.IsGSPEligibleLookup,
    mixins_serializer.IsTPPEligibleLookup,
    serializers.ModelSerializer
):
    r"""
    Serializer for master table
    """

    id = serializers.IntegerField(read_only=True)

    class Meta:
        model = models.DimLocation
        fields = [
            'id',
            'region',
            'country',
            'country_code_a2',
            'country_code_a3',
            'is_gsp_eligible', 'is_gsp_eligible_read_only', # Write and read only fields
            'is_tpp_eligible', 'is_tpp_eligible_read_only', # Write and read only fields
        ]


class DimCustomerSerializer(
    serializers.ModelSerializer
):
    r"""
    Serializer for master table
    """

    id = serializers.IntegerField(read_only=True)

    class Meta:
        model = models.DimCustomer
        fields = model.get_form_field_names_tuple(model)


class DimProductClassSerializer(
    serializers.ModelSerializer
):
    r"""
    Serializer for master table
    """

    id = serializers.IntegerField(read_only=True)

    class Meta:
        model = models.DimProductClass
        fields = model.get_form_field_names_tuple(model)


class DimProductGenderSerializer(
    serializers.ModelSerializer
):
    r"""
    Serializer for master table
    """

    id = serializers.IntegerField(read_only=True)

    class Meta:
        model = models.DimProductGender
        fields = model.get_form_field_names_tuple(model)


class DimProductKeywordSerializer(
    serializers.ModelSerializer
):
    r"""
    Serializer for master table
    """

    id = serializers.IntegerField(read_only=True)

    class Meta:
        model = models.DimProductKeyword
        fields = model.get_form_field_names_tuple(model)


class DimProductSizeRangeSerializer(
    serializers.ModelSerializer
):
    r"""
    Serializer for master table
    """

    id = serializers.IntegerField(read_only=True)

    class Meta:
        model = models.DimProductSizeRange
        fields = model.get_form_field_names_tuple(model)


class DimProductSubclassSerializer(
    serializers.ModelSerializer
):
    r"""
    Serializer for master table
    """

    id = serializers.IntegerField(read_only=True)

    class Meta:
        model = models.DimProductSubclass
        fields = model.get_form_field_names_tuple(model)


class DimProductTypeSerializer(
    serializers.ModelSerializer
):
    r"""
    Serializer for master table
    """

    id = serializers.IntegerField(read_only=True)

    class Meta:
        model = models.DimProductType
        fields = model.get_form_field_names_tuple(model)


class DimSeasonSerializer(
    mixins_serializer.YearLookup,
    serializers.ModelSerializer
):
    r"""
    Serializer for master table
    """

    id = serializers.IntegerField(read_only=True)

    class Meta:
        model = models.DimSeason
        fields = model.get_form_field_names_tuple(model)


class DimFabricSerializer(
    mixins_serializer.YearLookup,
    serializers.ModelSerializer
):
    r"""
    Serializer for master table
    """

    id = serializers.IntegerField(read_only=True)

    class Meta:
        model = models.DimFabric
        fields = model.get_form_field_names_tuple(model)


class DimVendorSerializer(
    mixins_serializer.DimLocationLookup,
    mixins_serializer.IsActiveLookup,
    serializers.ModelSerializer
):

    # Read-only fields
    id = serializers.IntegerField(read_only=True)

    class Meta:
        model = models.DimVendor
        fields = (
            'id',
            'dim_location', 'dim_location_read_only', # Write and read only fields
            'name',
            'code',
            'is_active', 'is_active_read_only', # Write and read only fields
        )


class HelperMappingSerializer(
    serializers.ModelSerializer
):
    r"""
    Serializer for master table
    """

    id = serializers.IntegerField(read_only=True)

    class Meta:
        model = models.HelperMapping
        fields = model.get_form_field_names_tuple(model)

    # Validation rules
    def validate(self, data):
        if (data['category'] == 'Vendor' and not
            models.DimVendor.objects.filter(code=data['parent']).exists()
        ):
            raise serializers.ValidationError('Value must exist in ' + data['category'] + ' master.')

        if (data['category'] == 'Customer' and not
            models.DimCustomer.objects.filter(name=data['parent']).exists()
        ):
            raise serializers.ValidationError('Value must exist in ' + data['category'] + ' master.')

        if (data['category'] == 'Product Type' and not
            models.DimProductType.objects.filter(name=data['parent']).exists()
        ):
            raise serializers.ValidationError('Value must exist in ' + data['category'] + ' master.')

        if (data['category'] == 'Product Class' and not
            models.DimProductClass.objects.filter(name=data['parent']).exists()
        ):
            raise serializers.ValidationError('Value must exist in ' + data['category'] + ' master.')

        if (data['category'] == 'Product Gender' and not
            models.DimProductGender.objects.filter(name=data['parent']).exists()
        ):
            raise serializers.ValidationError('Value must exist in ' + data['category'] + ' master.')

        if (data['category'] == 'Product Keyword' and not
            models.DimProductKeyword.objects.filter(name=data['parent']).exists()
        ):
            raise serializers.ValidationError('Value must exist in ' + data['category'] + ' master.')

        if (data['category'] == 'Product Size Range' and not
            models.DimProductSizeRange.objects.filter(name=data['parent']).exists()
        ):
            raise serializers.ValidationError('Value must exist in ' + data['category'] + ' master.')

        if (data['category'] == 'Product Subclass' and not
            models.DimProductSubclass.objects.filter(name=data['parent']).exists()
        ):
            raise serializers.ValidationError('Value must exist in ' + data['category'] + ' master.')

        if (data['category'] == 'Season' and not
            models.DimSeason.objects.filter(season=data['parent']).exists()
        ):
            raise serializers.ValidationError('Value must exist in ' + data['category'] + ' master.')

        return data

    def validate_category(self, value):
        value = value.title()
        valid_values = [
            'Vendor',
            'Customer',
            'Product Type',
            'Product Class',
            'Product Gender',
            'Product Keyword',
            'Product Size Range',
            'Product Subclass',
        ]
        if value in valid_values:
            return value
        raise serializers.ValidationError('Value must be one of the following: ' + ', '.join(map(str, valid_values)))
