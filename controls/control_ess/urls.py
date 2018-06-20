from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^$', views.BaseView.as_view(), name='base'),

    # Source data
    url(r'^source_tab$', views.SourceView.as_view(), name='source_tab'),

    # Profile and Settings
    url(r'^user_profile_tab$', views.ProfileView.as_view(), name='user_profile_tab'),
]
