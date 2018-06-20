from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^$', views.BaseView.as_view(), name='base'),

    # Search
    url(r'^search_tab$', views.SearchResultsViewDefault.as_view(), name='search_tab'),
    url(r'^search_tab_one_product/(?P<pk>\d+)$', views.SearchResultsViewOneProduct.as_view(), name='search_tab_one_product'),
    url(r'^search_tab_multiple_product/(?P<keyword>.+)$', views.SearchResultsViewMultipleProduct.as_view(), name='search_tab_multiple_product'),
    url(r'^search_tab_one_vendor/(?P<pk>\d+)$', views.SearchResultsViewOneVendor.as_view(), name='search_tab_one_vendor'),
    url(r'^search_tab_multiple_vendor/(?P<keyword>.+)$', views.SearchResultsViewMultipleVendor.as_view(), name='search_tab_multiple_vendor'),
    url(r'^search_tab_one_sample/(?P<pk>\d+)$', views.SearchResultsViewOneSample.as_view(), name='search_tab_one_sample'),
    url(r'^search_tab_multiple_sample/(?P<keyword>.+)$', views.SearchResultsViewMultipleSample.as_view(), name='search_tab_multiple_sample'),

    # Dashboard
    url(r'^dashboard_tab$', views.DashboardView.as_view(), name='dashboard_tab'),

    # # Image matching
    url(r'^image_matching_tab$', views.ImageMatchingView.as_view(), name='image_matching_tab'),

    # Operations
    url(r'^product_allocation_tab$', views.ProductAllocationView.as_view(), name='product_allocation_tab'),
    url(r'^product_allocation_confirmed_tab$', views.ProductAllocationViewConfirmed.as_view(), name='product_allocation_confirmed_tab'),
    url(r'^product_allocation_confirmed_xts_tab$', views.ProductAllocationViewConfirmedXTS.as_view(), name='product_allocation_confirmed_xts_tab'),

    # Test report
    url(r'^qc_report_tab$', views.QCReportView.as_view(), name='qc_report_tab'),

    # Master
    url(r'^master_table_tab/(?P<item>[\w]+)$', views.MasterTableView.as_view(), name='master_table_tab'),

    # Profile
    url(r'^user_profile_tab$', views.ProfileView.as_view(), name='user_profile_tab'),
]
