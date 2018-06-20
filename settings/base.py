import os
import sys

from django.urls import reverse_lazy


# Directory path variables
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SETTINGS_DIR = os.path.abspath(os.path.dirname(__file__))

# URL variables
STATIC_URL = '/static/'
STATIC_IMAGE_URL = 'static/'
CORE_JS_URL = os.path.join(STATIC_URL, 'core/custom/')
LOGIN_URL= reverse_lazy('login')
LOGIN_REDIRECT_URL = reverse_lazy('base')
LOGOUT_REDIRECT_URL = LOGIN_URL

# WSGI
WSGI_APPLICATION = 'settings.wsgi.application'

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'rest_framework',
    'widget_tweaks',
    'django.contrib.sites',
    'axes',
    'password_policies',
    'session_security',
    'blocks',
    'apps.standards.app_user',
    'apps.standards.app_error',
    'apps.standards.app_authentication',
    'apps.standards.app_ux',
]

# Middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Templates
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'builtins': [
                'blocks.templatetags.custom_filters',
            ],
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'core.context_processors.template_variables',
                'password_policies.context_processors.password_status',
            ],
        },
    },
]

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Security DRF
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    )
}

# Static files (CSS, JavaScript, Images)
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static")
]

# Logging
# LOGGING = {
#     'version': 1,
#     'disable_existing_loggers': True,
#     'formatters': {
#         'standard': {
#             'format' : "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
#             'datefmt' : "%d/%b/%Y %H:%M:%S"
#         },
#     },
#     'handlers': {
#         # 'null': {
#         #     'level':'DEBUG',
#         #     'class':'django.utils.log.NullHandler',
#         # },
#         'logfile': {
#             'level':'DEBUG',
#             'class':'logging.handlers.RotatingFileHandler',
#             'filename': os.path.join(SETTINGS_DIR, 'logs', 'application.log'),
#             'maxBytes': 1024*1024*5, # 5MB
#             'backupCount': 10,
#             'formatter': 'standard',
#         },
#         'console':{
#             'level':'INFO',
#             'class':'logging.StreamHandler',
#             'formatter': 'standard'
#         },
#     },
#     'loggers': {
#         'django': {
#             'handlers': ['console', 'logfile'],
#             # 'propagate': True,
#             'level':'INFO',
#             'formatter': 'verbose',
#         },
#         'django.db.backends': {
#             'handlers': ['console'],
#             'level': 'DEBUG',
#             'propagate': False,
#         },
#     }
# }


# Core JS and CSS frameworks
EMBEDDED_LIB_CORE = [
    'jquery',
    'boostrap',
    'font-awesome',
    'nprogress',
    'moment',
    'session_security',
    'fastclick',
    'function_library',
]


# Django Password security policies
SESSION_SERIALIZER = 'django.contrib.sessions.serializers.PickleSerializer'
SITE_ID = 1

# Session expiration
SESSION_SECURITY_WARN_AFTER = 60 * 28
SESSION_SECURITY_EXPIRE_AFTER = 60 * 29
SESSION_COOKIE_AGE = 60 * 30
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# Django Axes (track failed login attempts)
AXES_FAILURE_LIMIT = 5 # block user after 5 attempts from same IP
AXES_USE_USER_AGENT = False # lock out / log based on an IP address AND a user agent
AXES_LOCK_OUT_BY_COMBINATION_USER_AND_IP = False # prevents the login from IP under a particular user if the attempt limit has been exceeded, otherwise lock out based on IP
AXES_COOLOFF_TIME = 1 # defines a period of inactivity after which old failed login attempts will be forgotten
AXES_LOCKOUT_URL = reverse_lazy('account_locked')

# Django Password security policies
REDIRECT_FIELD_NAME = reverse_lazy('password_change')
PASSWORD_DURATION_SECONDS = 60 * 60 * 24 * 90 # Force password change after 90 days
PASSWORD_CHECK_ONLY_AT_LOGIN = False
PASSWORD_MIN_LENGTH = 8
PASSWORD_MIN_LETTERS = 3
PASSWORD_MIN_LETTERS_LOWER = 0
PASSWORD_MIN_LETTERS_UPPER = 0
PASSWORD_MIN_NUMBERS = 1
PASSWORD_MIN_SYMBOLS = 1
PASSWORD_MAX_CONSECUTIVE = 3
PASSWORD_USE_CRACKLIB = True
PASSWORD_USE_HISTORY = True
PASSWORD_HISTORY_COUNT = 4
PASSWORD_DIFFERENCE_DISTANCE = 3 # A minimum distance of the difference between old and new password. A positive integer. Values greater than 1 are recommended.
PASSWORD_COMMON_SEQUENCES = [u'0123456789', u'`1234567890-=', u'~!@#$%^&*()_+', u'abcdefghijklmnopqrstuvwxyz', u"quertyuiop[]\\asdfghjkl;'zxcvbnm,./", u'quertyuiop{}|asdfghjkl;"zxcvbnm<>?', u'quertyuiopasdfghjklzxcvbnm', u"1qaz2wsx3edc4rfv5tgb6yhn7ujm8ik,9ol.0p;/-['=]\\", u'qazwsxedcrfvtgbyhnujmikolp']

# Smart data pipeline engine
DEFAULT_SIZE = 500
INT_LIMIT = 1000000000
FORMAT_DATES = {
    # MM/DD/YYYY
    'DATE_US': r"""^(?:0?[1-9]|1[0-2])[/-](?:(?:0[1-9])|(?:[12][0-9])|(?:3[01])|[1-9])[/-](?:\d\d){1,2}""",
    # DD/MM/YYYY
    'DATE_EU': r"""^(?:(?:0[1-9])|(?:[12][0-9])|(?:3[01])|[1-9])[./-](?:0?[1-9]|1[0-2])[./-](?:\d\d){1,2}""",
    # YYYY/MM/DD
    'DATE_ISO': r"""^(?:\d{4})[./-]?(?:0?[1-9]|1[0-2])[./-](?:(?:0[1-9])|(?:[12][0-9])|(?:3[01])|[1-9])""",
    # MM/YYYY
    'MONTH_DATE': r"""^(?:0?[1-9]|1[0-2])[./-](?:\d\d){1,2}$""",
    # YYYY/MM
    'MONTH_DATE_ISO': r"""^(?:\d{4})[./-]?(?:0?[1-9]|1[0-2])$"""
}
FORMAT_FLOAT = r"""^\d+(,\d+)*\.\d+%?$"""
FORMAT_INT = r"""^\d+(,\d+)*%?$"""
