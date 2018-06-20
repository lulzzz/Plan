from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns

from . import views

urlpatterns = [

    # Source files
    url(r'^metadata_table$', views.SourceExtractTable.as_view(), name='metadata_table'),

]

urlpatterns = format_suffix_patterns(urlpatterns)
