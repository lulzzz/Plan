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

    # Dashboard
    url(r'^dashboard_tab$', views.DashboardView.as_view(), name='dashboard_tab'),

    # Reports
    url(r'^report01_tab$', views.Report01View.as_view(), name='report01_tab'),
    url(r'^report02_tab$', views.Report02View.as_view(), name='report02_tab'),
    url(r'^report03_tab$', views.Report03View.as_view(), name='report03_tab'),

    # PDAS
    url(r'^master_table_tab/(?P<item>[\w]+)$', views.MasterTableView.as_view(), name='master_table_tab'),
    url(r'^procedure_tab$', views.ProcedureView.as_view(), name='procedure_tab'),
    url(r'^source_data_tab$', views.SourceDataView.as_view(), name='source_data_tab'),

    # Profile and Settings
    url(r'^user_profile_tab$', views.ProfileView.as_view(), name='user_profile_tab'),
]
