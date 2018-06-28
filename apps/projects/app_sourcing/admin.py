from django.contrib import admin

from .models import DimCustomer
from .models import DimFabric
from .models import DimLocation
from .models import DimProduct
from .models import DimProductClass
from .models import DimProductGender
from .models import DimProductKeyword
from .models import DimProductSizeRange
from .models import DimProductSubclass
from .models import DimProductType
from .models import DimSeason
from .models import DimVendor
from .models import HelperMapping
from .models import HelperMatchingCriteria
from .models import DimProductImageAssociation

# DimCustomer
class DimCustomerAdmin(admin.ModelAdmin):

    list_display = ('name', 'code')
    search_fields = ('name', 'code')

admin.site.register(DimCustomer, DimCustomerAdmin)


# DimLocation
class DimLocationAdmin(admin.ModelAdmin):

    list_display = (
        'region',
        'country',
        'country_code_a2',
        'country_code_a3'
    )
    search_fields = (
        'region',
        'country',
        'country_code_a2',
        'country_code_a3'
    )
    list_filter = (
        ('region', admin.AllValuesFieldListFilter),
    )

admin.site.register(DimLocation, DimLocationAdmin)


# DimProduct
class DimProductAdmin(admin.ModelAdmin):

    list_display = (
        'style',
        'silhouette',
        'get_dim_product_gender',
    )
    search_fields = ('style', 'silhouette', 'silhouette')
    list_filter = (
        ('dim_product_gender__name', admin.AllValuesFieldListFilter),
    )

    def get_dim_product_gender(self, obj):
        return obj.dim_product_gender.name

    get_dim_product_gender.short_description = 'Gender'
    get_dim_product_gender.admin_order_field = 'dim_product_gender__name'

admin.site.register(DimProduct, DimProductAdmin)


# DimProductImageAssociation
class DimProductImageAssociationAdmin(admin.ModelAdmin):

    list_display = (
        'get_dim_product_style',
        'category',
        'relative_path',
    )
    search_fields = ('dim_product__style',)
    list_filter = (
        ('category', admin.AllValuesFieldListFilter),
    )

    def get_dim_product_style(self, obj):
        return obj.dim_product.style

    get_dim_product_style.short_description = 'Style'
    get_dim_product_style.admin_order_field = 'dim_product__style'

admin.site.register(DimProductImageAssociation, DimProductImageAssociationAdmin)


# DimVendor
class DimVendorAdmin(admin.ModelAdmin):

    list_display = (
        'name',
        'code',
        'is_active',
        'get_dim_location_country',
    )
    search_fields = (
        'name',
        'code',
        'dim_location__country',
    )
    list_filter = (
        ('is_active', admin.BooleanFieldListFilter),
    )

    def get_dim_location_country(self, obj):
        return obj.dim_location.country

    get_dim_location_country.short_description = 'Country'
    get_dim_location_country.admin_order_field = 'dim_location__country'

admin.site.register(DimVendor, DimVendorAdmin)


# HelperMatchingCriteria
class HelperMatchingCriteriaAdmin(admin.ModelAdmin):

    list_display = (
        'table_name',
        'field_name',
        'matching_priority',
        'matching_level',
    )

admin.site.register(HelperMatchingCriteria, HelperMatchingCriteriaAdmin)
