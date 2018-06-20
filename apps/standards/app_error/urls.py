from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^account_locked$', views.handler401, name='account_locked'),
    url(r'^password_change$', views.password_change, name='password_change'),
]
