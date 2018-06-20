from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^$', views.BaseView.as_view(), name='base'),

    # Magic
    url(r'^magic_tab$', views.MagicView.as_view(), name='magic_tab'),

    # Profile and Settings
    url(r'^user_profile_tab$', views.ProfileView.as_view(), name='user_profile_tab'),
]
