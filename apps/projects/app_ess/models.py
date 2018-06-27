from django.db import models
from django.urls import reverse
from django.core.validators import RegexValidator
from django.contrib.auth.models import User

from core import mixins_model


class DimCustomer(models.Model, mixins_model.ModelFormFieldNames):
    name = models.CharField(verbose_name='customer', max_length=100, unique=True)
    code = models.CharField(max_length=30, unique=True)

    form_field_list = [
        'id',
        'name',
        'code',
    ]

    class Meta:
        verbose_name = 'Customer'

    def __str__(self):
        return str(self.name)


class DimLocation(models.Model, mixins_model.ModelFormFieldNames):
    region = models.CharField(max_length=45)
    country = models.CharField(unique=True, max_length=100)
    country_code_a2 = models.CharField(verbose_name='country code A2', unique=True, max_length=2, validators=[RegexValidator(regex='^.{2}$', message='Length must be 2', code='nomatch')])
    country_code_a3 = models.CharField(verbose_name='country code A3', unique=True, max_length=3, validators=[RegexValidator(regex='^.{3}$', message='Length must be 3', code='nomatch')])
    is_gsp_eligible = models.BooleanField(verbose_name='is GSP eligible')
    is_tpp_eligible = models.BooleanField(verbose_name='is TPP eligible')

    form_field_list = [
        'id',
        'region',
        'country',
        'country_code_a2',
        'country_code_a3',
        'is_gsp_eligible',
        'is_tpp_eligible',
    ]

    class Meta:
        verbose_name = 'Location'
        ordering = ['country']

    def __str__(self):
        return self.country

class DimSeason(models.Model, mixins_model.ModelFormFieldNames):
    season_id = models.IntegerField()
    year = models.IntegerField()
    season = models.CharField(max_length=30)
    season_short = models.CharField(max_length=30)

    form_field_list = [
        'id',
        'year',
        'season',
        'season_short',
    ]

    class Meta:
        verbose_name = 'Season'
        unique_together = (('year', 'season'),)
        ordering = ['year', 'season']

    def __str__(self):
        return str(self.year) + ' ' + self.season


class DimProduct(models.Model, mixins_model.ModelFormFieldNames):
    source_name = models.CharField(max_length=300, blank=True, null=True)
    image_relative_path = models.CharField(verbose_name='image', max_length=500, blank=True, null=True)
    style = models.CharField(max_length=100, unique=True)
    silhouette = models.CharField(max_length=45, blank=True, null=True)
    fabric_weight = models.CharField(max_length=45, blank=True, null=True)
    fabric_class = models.CharField(max_length=45, blank=True, null=True)
    description = models.CharField(max_length=500, blank=True, null=True)
    dim_season = models.ForeignKey(DimSeason, models.DO_NOTHING)
    dim_customer = models.ForeignKey(DimCustomer, models.DO_NOTHING)
    dim_fabric = models.ForeignKey('DimFabric', models.DO_NOTHING)
    dim_product_gender = models.ForeignKey('DimProductGender', models.DO_NOTHING)
    dim_product_type = models.ForeignKey('DimProductType', models.DO_NOTHING)
    dim_product_class = models.ForeignKey('DimProductClass', models.DO_NOTHING)
    dim_product_subclass = models.ForeignKey('DimProductSubclass', models.DO_NOTHING)
    dim_product_keywords = models.ManyToManyField('DimProductKeyword', verbose_name='keywords')
    dim_product_sizes = models.ManyToManyField('DimProductSizeRange', verbose_name='sizes')
    dim_vendor = models.ForeignKey('DimVendor', models.DO_NOTHING)
    fob = models.FloatField(verbose_name='FOB', blank=True, null=True)
    is_approved = models.BooleanField(default=False)
    is_selected = models.BooleanField(default=False)
    # is_placeholder = models.BooleanField(default=False)
    # is_test_sample = models.BooleanField(default=False)

    form_field_list = [
        'id',
        'style',
        'silhouette',
        'description',
        'fabric_weight',
        'fabric_class'
        'dim_season',
        'dim_customer',
        'dim_fabric',
        'dim_product_gender',
        'dim_product_type',
        'dim_product_class',
        'dim_product_subclass',
        'dim_vendor',
        'fob',
    ]

    class Meta:
        verbose_name = 'Product'

    def get_absolute_url(self):
        return reverse(
            'search_tab_one_product',
            kwargs={'pk': self.pk}
        )

    @property
    def url(self):
        return self.get_absolute_url().replace('/', '#', 1)

    @property
    def image_link(self):
        return {
            'menu_item': 'search',
            'name': 'search_tab_one_product' + str(self.pk),
            'link': self.get_absolute_url().replace('/', '#', 1),
            'image': self.image_relative_path
        }

    def __str__(self):
        return self.style


class DimFabric(models.Model, mixins_model.ModelFormFieldNames):
    material_code = models.CharField(max_length=100, unique=True)
    material_group = models.CharField(max_length=100)
    description = models.CharField(max_length=500, blank=True, null=True)
    fiber_content = models.CharField(max_length=100, blank=True, null=True)
    construction = models.CharField(max_length=100, blank=True, null=True)
    material_type = models.CharField(max_length=100, blank=True, null=True)
    material_subtype = models.CharField(max_length=100, blank=True, null=True)
    material_class = models.CharField(max_length=100, blank=True, null=True)
    material_class_remark = models.CharField(max_length=100, blank=True, null=True)
    weight = models.CharField(max_length=30, blank=True, null=True)
    weight_uom = models.CharField(verbose_name='weight UOM', max_length=100, blank=True, null=True)
    width = models.CharField(max_length=30, blank=True, null=True)
    width_uom = models.CharField(verbose_name='width UOM', max_length=100, blank=True, null=True)

    form_field_list = [
        'id',
        'material_code',
        'material_group',
        'description',
        'fiber_content',
        'construction',
        'material_type',
        'material_subtype',
        'material_class',
        'material_class_remark',
        'weight',
        'weight_uom',
        'width',
        'width_uom',
    ]

    class Meta:
        verbose_name = 'Fabric'
        ordering = ['material_code']

    def __str__(self):
        return self.material_code


class DimMaterial(models.Model, mixins_model.ModelFormFieldNames):
    # Many to Many
    dim_product = models.ManyToManyField(DimProduct)

    fiber_content = models.CharField(max_length=100, unique=True)
    fiber_construction = models.CharField(max_length=100, blank=True, null=True)
    yarn_size = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        verbose_name = 'Material'
        unique_together = (('fiber_content', 'fiber_construction', 'yarn_size'),)

    def __str__(self):
        return self.fiber_content


class DimProductClass(models.Model, mixins_model.ModelFormFieldNames):
    name = models.CharField(verbose_name='class', max_length=100, unique=True)
    description = models.CharField(max_length=500, blank=True, null=True)

    form_field_list = [
        'id',
        'name',
        'description',
    ]

    class Meta:
        verbose_name = 'Product Class'
        ordering = ['name']

    def __str__(self):
        return self.name


class DimProductGender(models.Model, mixins_model.ModelFormFieldNames):
    name = models.CharField(verbose_name='gender', max_length=100, unique=True)
    description = models.CharField(max_length=500, blank=True, null=True)

    form_field_list = [
        'id',
        'name',
        'description',
    ]

    class Meta:
        verbose_name = 'Product Gender'
        ordering = ['name']

    def __str__(self):
        return self.name


class DimProductImageAssociation(models.Model, mixins_model.ModelFormFieldNames):
    dim_product = models.ForeignKey(DimProduct, models.DO_NOTHING)
    category = models.CharField(max_length=30)
    relative_path = models.CharField(max_length=500)
    absolute_path = models.CharField(max_length=500)

    class Meta:
        verbose_name = 'Product image association'


class DimProductKeyword(models.Model, mixins_model.ModelFormFieldNames):
    name = models.CharField(verbose_name='keyword', max_length=100, unique=True)
    description = models.CharField(max_length=500, blank=True, null=True)

    form_field_list = [
        'id',
        'name',
        'description',
    ]

    class Meta:
        verbose_name = 'Product Keyword'
        ordering = ['name']

    def __str__(self):
        return self.name


class DimProductSizeRange(models.Model, mixins_model.ModelFormFieldNames):
    name = models.CharField(verbose_name='size range', max_length=100, unique=True)
    description = models.CharField(max_length=500, blank=True, null=True)

    form_field_list = [
        'id',
        'name',
        'description',
    ]

    class Meta:
        verbose_name = 'Product Size Range'
        ordering = ['name']

    def __str__(self):
        return str(self.name)


class DimProductSubclass(models.Model, mixins_model.ModelFormFieldNames):
    name = models.CharField(verbose_name='subclass', max_length=100, unique=True)
    description = models.CharField(max_length=500, blank=True, null=True)

    form_field_list = [
        'id',
        'name',
        'description',
    ]

    class Meta:
        verbose_name = 'Product Subclass'
        ordering = ['name']

    def __str__(self):
        return self.name


class DimProductType(models.Model, mixins_model.ModelFormFieldNames):
    name = models.CharField(verbose_name='type', max_length=100, unique=True)
    description = models.CharField(max_length=500, blank=True, null=True)

    form_field_list = [
        'id',
        'name',
        'description',
    ]

    class Meta:
        verbose_name = 'Product Type'
        ordering = ['name']

    def __str__(self):
        return self.name

class DimVendor(models.Model, mixins_model.ModelFormFieldNames):
    dim_location = models.ForeignKey(DimLocation, models.DO_NOTHING, verbose_name='country')
    name = models.CharField(verbose_name='vendor name', max_length=100, unique=True)
    code = models.CharField(verbose_name='vendor code', max_length=30, unique=True)
    is_active = models.BooleanField()

    form_field_list = [
        'id',
        'dim_location',
        'name',
        'code',
        'is_active',
    ]

    class Meta:
        verbose_name = 'Vendor'
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse(
            'search_tab_one_vendor',
            kwargs={'pk': self.pk}
        )

    @property
    def url(self):
        return self.get_absolute_url().replace('/', '#', 1)

    @property
    def link(self):
        return {
            'menu_item': 'search',
            'name': 'search_tab_one_vendor' + str(self.pk),
            'link': self.get_absolute_url().replace('/', '#', 1),
        }


class FactAllocation(models.Model, mixins_model.ModelFormFieldNames):
    dim_product = models.ForeignKey(DimProduct, models.DO_NOTHING)
    dim_product_matching = models.ForeignKey(DimProduct, models.DO_NOTHING, related_name='dim_product_matching')
    dim_season = models.ForeignKey(DimSeason, models.DO_NOTHING)
    dim_vendor = models.ForeignKey(DimVendor, models.DO_NOTHING)
    allocation_type = models.CharField(max_length=100)
    priority = models.IntegerField()
    ship_date = models.DateField(blank=True, null=True)
    fob = models.FloatField(verbose_name='FOB', blank=True, null=True)
    quantity = models.IntegerField(blank=True, null=True)
    comment = models.CharField(max_length=500, blank=True, null=True)
    matching_logic = models.CharField(max_length=1000, blank=True, null=True)
    matching_level = models.CharField(max_length=100, blank=True, null=True)
    similarity = models.FloatField(blank=True, null=True)
    is_approved = models.BooleanField()
    is_selected = models.BooleanField()

    form_field_list = [
        'id',
        'allocation_type',
        [
            'dim_product',
            [
                'style',
                'silhouette',
            ],
        ],
        [
            'dim_season',
            [
                'year',
                'season',
            ],
        ],
        [
            'dim_vendor',
            [
                'name',
            ],
        ],
        'ship_date',
        'fob',
        'quantity',
        'comment',
        'matching_logic',
        'matching_level',
    ]

    class Meta:
        verbose_name = 'Allocation'

    @property
    def radiobox(self):
        return {
            'id': self.id,
            'url': reverse(
                'matching_product_selection',
                kwargs={
                    'pk': self.pk,
                    'dim_product_id': self.dim_product.id,
                    'dim_product_matching_id': self.dim_product_matching.id,
                }
            ),
            'url_pk': self.dim_product_matching.id,
            'is_selected': self.is_selected
        }
