from settings.urls import *
from django.conf.urls import include, url


urlpatterns.append(url(r'', include('controls.control_ess.urls'), name='base'))
urlpatterns.append(url(r'^pipeline/', include('apps.standards.app_pipeline.urls')))
