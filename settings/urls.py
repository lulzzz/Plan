from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^admin/', admin.site.urls),
    url(r'^session_security/', include('session_security.urls')),
    url(r'^error/', include('apps.standards.app_error.urls')),
    url(r'^authentication/', include('apps.standards.app_authentication.urls')),
    url(r'^user/', include('apps.standards.app_user.urls')),
    url(r'^ux/', include('apps.standards.app_ux.urls')),
]

# Error pages
handler400 = 'apps.standards.app_error.views.handler400'
handler403 = 'apps.standards.app_error.views.handler403'
handler404 = 'apps.standards.app_error.views.handler404'
handler500 = 'apps.standards.app_error.views.handler500'

# Admin pages
admin.site.site_header = 'Datacrag Administration'
