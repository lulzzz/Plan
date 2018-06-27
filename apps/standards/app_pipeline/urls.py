from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns

from . import views

urlpatterns = [

    # Source files
    url(r'^metadata_table$', views.SourceExtractTable.as_view(), name='metadata_table'),

    # Row and column count
    url(r'^metadata_row_count$', views.RowChartAPI.as_view(), name='metadata_row_count'),
    url(r'^metadata_col_count$', views.ColChartAPI.as_view(), name='metadata_col_count'),

]

urlpatterns = format_suffix_patterns(urlpatterns)
