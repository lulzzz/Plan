from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^user_details/$', views.BasicDetails.as_view(), name='user_details'),
    url(r'^user_password/$', views.PasswordChange.as_view(), name='user_password'),
]
