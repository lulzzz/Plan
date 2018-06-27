from rest_framework import serializers

from . import models


class DimLocationLookup(serializers.Serializer):
    r"""
    Validation mixin that does a lookup for finding country code A2 for dim_location_id
    """

    # Read-only field
    dim_location_read_only = serializers.SerializerMethodField()

    # Write-only fields
    dim_location = serializers.CharField(write_only=True)

    # Read-only methods (get_ is a DRF prefix)
    def get_dim_location_read_only(self, obj):
        return obj.dim_location.country

    # Validation rules
    def validate_dim_location(self, value):
        value = value.title()
        model_item = models.DimLocation.objects.filter(country=value)
        if model_item.count() > 0:
            return model_item.first()
        raise serializers.ValidationError('Value must exist in location master')


class DimChannelLookup(serializers.Serializer):
    r"""
    Validation mixin that does a lookup for finding name for dim_channel
    """

    # Read-only field
    dim_channel_read_only = serializers.SerializerMethodField()

    # Write-only fields
    dim_channel = serializers.CharField(write_only=True)

    # Read-only methods (get_ is a DRF prefix)
    def get_dim_channel_read_only(self, obj):
        return obj.dim_channel.name

    # Validation rules
    def validate_dim_channel(self, value):
        model_item = models.DimChannel.objects.filter(name=value)
        if model_item.count() > 0:
            return model_item.first()
        raise serializers.ValidationError('Value must exist in channel master')


class IsGSPEligibleLookup(serializers.Serializer):
    r"""
    Validation mixin that does the boolean field conversion
    """

    # Read-only field
    is_gsp_eligible_read_only = serializers.SerializerMethodField()

    # Write-only fields
    is_gsp_eligible = serializers.CharField(write_only=True)

    # Read-only methods (get_ is a DRF prefix)
    def get_is_gsp_eligible_read_only(self, obj):
        return 'Y' if obj.is_gsp_eligible else 'N'

    # Validation rules
    def validate_is_gsp_eligible(self, value):
        value = value[:1].upper()
        valid_values = ['Y', 'N']
        if value in valid_values:
            return True if value == 'Y' else False
        raise serializers.ValidationError('Value must be one of the following: ' + ', '.join(map(str, valid_values)))

class IsTPPEligibleLookup(serializers.Serializer):
    r"""
    Validation mixin that does the boolean field conversion
    """

    # Read-only field
    is_tpp_eligible_read_only = serializers.SerializerMethodField()

    # Write-only fields
    is_tpp_eligible = serializers.CharField(write_only=True)

    # Read-only methods (get_ is a DRF prefix)
    def get_is_tpp_eligible_read_only(self, obj):
        return 'Y' if obj.is_tpp_eligible else 'N'

    # Validation rules
    def validate_is_tpp_eligible(self, value):
        value = value[:1].upper()
        valid_values = ['Y', 'N']
        if value in valid_values:
            return True if value == 'Y' else False
        raise serializers.ValidationError('Value must be one of the following: ' + ', '.join(map(str, valid_values)))


class IsActiveLookup(serializers.Serializer):
    r"""
    Validation mixin that does the boolean field conversion
    """

    # Read-only field
    is_active_read_only = serializers.SerializerMethodField()

    # Write-only fields
    is_active = serializers.CharField(write_only=True)

    # Read-only methods (get_ is a DRF prefix)
    def get_is_active_read_only(self, obj):
        return 'Y' if obj.is_active else 'N'

    # Validation rules
    def validate_is_active(self, value):
        value = value[:1].upper()
        valid_values = ['Y', 'N']
        if value in valid_values:
            return True if value == 'Y' else False
        raise serializers.ValidationError('Value must be one of the following: ' + ', '.join(map(str, valid_values)))


class IsPlaceholderLookup(serializers.Serializer):
    r"""
    Validation mixin that does the boolean field conversion
    """

    # Read-only field
    is_placeholder_read_only = serializers.SerializerMethodField()

    # Write-only fields
    is_placeholder = serializers.CharField(write_only=True)

    # Read-only methods (get_ is a DRF prefix)
    def get_is_placeholder_read_only(self, obj):
        return 'Y' if obj.is_placeholder else 'N'

    # Validation rules
    def validate_is_placeholder(self, value):
        value = value[:1].upper()
        valid_values = ['Y', 'N']
        if value in valid_values:
            return True if value == 'Y' else False
        raise serializers.ValidationError('Value must be one of the following: ' + ', '.join(map(str, valid_values)))


class YearLookup(serializers.Serializer):
    r"""
    Validation mixin that checks if value between 2 integers
    """

    # Validation rules
    def validate_year(self, value):
        valid_values = range(2000, 2051)
        if value in valid_values:
            return value
        raise serializers.ValidationError('Value must be between {} and {}.'.format(valid_values[0], valid_values[-1]))



class RegionLookup(serializers.Serializer):
    r"""
    Validation mixin that checks the region value
    """

    # Validation rules
    def validate_region(self, value):
        value = value.upper()
        valid_values = ['EMEA', 'APAC', 'AMER']
        if value in valid_values:
            return value
        raise serializers.ValidationError('Value must be one of the following: ' + ', '.join(map(str, valid_values)))


class CountryCodeA2Lookup(serializers.Serializer):
    r"""
    Validation mixin that checks the country code A2
    """

    # Validation rules
    def validate_country_code_a2(self, value):
        if models.DimLocation.objects.filter(country_code_a2=value).exists():
            return value
        raise serializers.ValidationError('Value must exist in location master')
