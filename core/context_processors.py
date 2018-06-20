from django.conf import settings

def template_variables(request):
    return {
        'CSS_URL': settings.THEME_URL + 'css/',
        'JS_URL': settings.THEME_URL + 'js/',
        'CORE_JS_URL': settings.CORE_JS_URL,
        'MEDIA_URL': settings.THEME_URL + 'media/',
        'IMAGE_URL': settings.IMAGE_URL,
        'APPLICATION_NAME': settings.APPLICATION_NAME,
        'COMPANY_NAME': settings.COMPANY_NAME,
        'PROVIDER': settings.PROVIDER,
        'PROVIDER_WEBSITE_URL': settings.PROVIDER_WEBSITE_URL,
    }
