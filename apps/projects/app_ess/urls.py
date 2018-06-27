from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns

from . import views

urlpatterns = [
    url(r'^search_api/$', views.SearchAPI.as_view(), name='search_api'),
    url(r'^search_api/(?P<query>[\w\-\s()]+)/$', views.SearchAPI.as_view(), name='search_api'),

    url(r'^search_result_product/(?P<keyword>.+)/$', views.SearchResultProduct.as_view(), name='search_result_product'),
    url(r'^search_result_vendor/(?P<keyword>.+)/$', views.SearchResultVendor.as_view(), name='search_result_vendor'),
    url(r'^search_result_sample/(?P<keyword>.+)/$', views.SearchResultSample.as_view(), name='search_result_sample'),

    url(r'^handsontable/(?P<item>[\w]+)/$', views.MasterTableAPI.as_view(), name='handsontable'), # For DRF page
    url(r'^handsontable_header/(?P<item>[\w]+)/$', views.MasterTableHeaderAPI.as_view(), name='handsontable_header'), # For DRF page

    url(r'^allocation_by_priority_api$', views.AllocationByPriorityAPI.as_view(), name='allocation_by_priority_api'),
    url(r'^allocation_by_gender_api$', views.AllocationByGenderAPI.as_view(), name='allocation_by_gender_api'),
    url(r'^allocation_by_product_type_api$', views.AllocationByProductTypeAPI.as_view(), name='allocation_by_product_type_api'),
    url(r'^allocation_by_coo_api$', views.AllocationByCOOAPI.as_view(), name='allocation_by_coo_api'),
    url(r'^products_by_customer_api$', views.ProductsByCustomerAPI.as_view(), name='products_by_customer_api'),

    url(r'^allocation_by_vendor_confirmed$', views.AllocationByVendorConfirmed.as_view(), name='allocation_by_vendor_confirmed'),
    url(r'^allocation_by_vendor_non_confirmed$', views.AllocationByVendorNonConfirmed.as_view(), name='allocation_by_vendor_non_confirmed'),

    # All products
    url(r'^allocation_confirmed$', views.AllocationConfirmed.as_view(), name='allocation_confirmed'),
    url(r'^allocation_confirmed_xts$', views.AllocationConfirmedXTS.as_view(), name='allocation_confirmed_xts'),
    url(r'^allocation_non_confirmed$', views.AllocationNonConfirmed.as_view(), name='allocation_non_confirmed'),

    url(r'^sample_test_report_table/(?P<pk>\d+)$', views.SampleTestReportTable.as_view(), name='sample_test_report_table'),

    # Specific product
    url(r'^allocation_specific_product/(?P<pk>\d+)$', views.AllocationSpecificProduct.as_view(), name='allocation_specific_product'),

    # Matched product selection
    url(r'^matching_product_selection/(?P<pk>\d+)/(?P<dim_product_id>\d+)/(?P<dim_product_matching_id>\d+)$', views.MatchingProductSelection.as_view(), name='matching_product_selection'),

    # Map
    url(r'^vendor_map$', views.VendorMap.as_view(), name='vendor_map'),
    url(r'^vendor_map/(?P<pk>\d+)$', views.VendorMap.as_view(), name='vendor_map'),
    url(r'^vendor_map_api$', views.VendorMapAPI.as_view(), name='vendor_map_api'),
    url(r'^vendor_map_api/(?P<pk>\d+)$', views.VendorMapAPI.as_view(), name='vendor_map_api'),
    url(r'^product_allocation_map$', views.ProductAllocationMap.as_view(), name='product_allocation_map'),
    url(r'^product_allocation_map_api$', views.ProductAllocationMapAPI.as_view(), name='product_allocation_map_api'),

    # Gallery
    url(r'^product_image_gallery$', views.ProductImageGallery.as_view(), name='product_image_gallery'),
    url(r'^product_image_gallery/(?P<pk>\d+)$', views.ProductImageGallery.as_view(), name='product_image_gallery'),
    url(r'^sample_image_gallery/(?P<pk>\d+)$', views.SampleImageGallery.as_view(), name='sample_image_gallery'),

    # Image matching
    url(r'^image_matching_view$', views.ImageMatchingView.as_view(), name='image_matching_view'),
    url(r'^image_matching_upload$', views.ImageMatchingUpload.as_view(), name='image_matching_upload'),
    url(r'^image_matching_display$', views.ImageMatchingDisplay.as_view(), name='image_matching_display'),
    url(r'^image_matching_result_table$', views.ImageMatchingResultTable.as_view(), name='image_matching_result_table'),
    url(r'^image_matching_result_table/(?P<pk>\d+)$', views.ImageMatchingResultTable.as_view(), name='image_matching_result_table'),

    # Attribute
    url(r'^product_attribute_table_selected_true$', views.ProductAttributeTableSelectedTrue.as_view(), name='product_attribute_table_selected_true'),
    url(r'^product_attribute_table_selected_true/(?P<pk>\d+)$', views.ProductAttributeTableSelectedTrue.as_view(), name='product_attribute_table_selected_true'),
    url(r'^product_attribute_table_selected_false$', views.ProductAttributeTableSelectedFalse.as_view(), name='product_attribute_table_selected_false'),
    url(r'^product_attribute_table_selected_false/(?P<pk>\d+)$', views.ProductAttributeTableSelectedFalse.as_view(), name='product_attribute_table_selected_false'),
    url(r'^vendor_attribute_table/(?P<pk>\d+)$', views.VendorAttributeTable.as_view(), name='vendor_attribute_table'),
    url(r'^sample_attribute_table/(?P<pk>\d+)$', views.SampleAttributeTable.as_view(), name='sample_attribute_table'),
    url(r'^allocation_confirmed_xts_vendor/(?P<pk>\d+)$', views.AllocationConfirmedXTSVendor.as_view(), name='allocation_confirmed_xts_vendor'),

    # Pivot
    url(r'^qc_report_pivottable$', views.QCReportPivotTable.as_view(), name='qc_report_pivottable'),
    url(r'^pass_fail_report_pivottable$', views.PassFailReportPivotTable.as_view(), name='pass_fail_report_pivottable'),
]

urlpatterns = format_suffix_patterns(urlpatterns)
