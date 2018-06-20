from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^master_table$', views.MasterTable.as_view(), name='master_table'),
    url(r'^chartjs$', views.ChartJS.as_view(), name='chartjs'),
    url(r'^combochartjs$', views.ComboChartJS.as_view(), name='combochartjs'),
    url(r'^pivottablejs$', views.PivotTableJS.as_view(), name='pivottablejs'),
]
