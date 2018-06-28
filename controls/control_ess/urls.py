from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^$', views.BaseView.as_view(), name='base'),

    # Dashboard
    url(r'^dashboard_tab$', views.DashboardView.as_view(), name='dashboard_tab'),

    # Source data
    url(r'^source_tab$', views.SourceView.as_view(), name='source_tab'),

    # Master
    url(r'^master_table_tab/(?P<item>[\w]+)$', views.MasterTableView.as_view(), name='master_table_tab'),

    # Profile and Settings
    url(r'^user_profile_tab$', views.ProfileView.as_view(), name='user_profile_tab'),
]
