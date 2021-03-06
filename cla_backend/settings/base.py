import datetime
import sys
import os
from os.path import join, abspath, dirname
import dj_database_url

# PATH vars

here = lambda *x: join(abspath(dirname(__file__)), *x)
PROJECT_ROOT = here("..")
root = lambda *x: join(abspath(PROJECT_ROOT), *x)

sys.path.insert(0, root('apps'))
sys.path.insert(0, root('libs'))


# ENVIRON values

from django.core.exceptions import ImproperlyConfigured

# .env_values.py contains secrets and host config values usually stored
# in a different place
try:
    import env_values
except ImportError:
    env_values = None


def get_env_value(var_name):
    """ Get the env value `var_name` or return exception """
    try:
        return getattr(env_values, var_name)
    except AttributeError:
        raise ImproperlyConfigured("Environment value %s not found" % var_name)


DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = ()

MANAGERS = ADMINS

EMAIL_FROM_ADDRESS = 'no-reply@civillegaladvice.service.gov.uk'

OPERATOR_USER_ALERT_EMAILS = []
SPECIALIST_USER_ALERT_EMAILS = []

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'cla_backend',
        'USER': 'postgres',
        'PASSWORD': '',
        'HOST': '',                      # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
        'PORT': '',                      # Set to empty string for default.
    }
}

# Support heroku
DJ_DATABASE_URL = os.environ.get('DATABASE_URL')
if DJ_DATABASE_URL:
    DATABASES =  {
        'default': dj_database_url.parse(DJ_DATABASE_URL)
    }

SITE_HOSTNAME = os.environ.get('SITE_HOSTNAME', 'cla.local:8000')

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
ALLOWED_HOSTS = []

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'Europe/London'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-gb'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = False

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/var/www/example.com/media/"
MEDIA_ROOT = root('assets', 'uploads')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = root('static')

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    root('assets'),
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'o=>4$)9?38N@^}d&pj,VL9^{r][xM9L.9cfE:xZZNk(N?v27+i'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

MIDDLEWARE_CLASSES = (
    'django_statsd.middleware.GraphiteRequestTimingMiddleware',
    'core.middleware.GraphiteMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'cla_backend.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'cla_backend.wsgi.application'

TEMPLATE_DIRS = (
    root('templates'),
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'django_statsd',
    'south',
    'rest_framework',
    'pagedown',
    'provider',
    'provider.oauth2',
    'reports'
)

PROJECT_APPS = (
    'core',
    'legalaid',
    'cla_provider',
    'call_centre',
    'cla_eventlog',
    'reports',
    'knowledgebase',
    'timer',
    'diagnosis',
    'status',
    'historic',
    'cla_auth'
)

INSTALLED_APPS += PROJECT_APPS

# DIAGNOSIS

DIAGNOSIS_FILE_NAME = 'graph-2014.07.21.graphml'


# DIVERSITY

DIVERSITY_PUBLIC_KEY_PATH = os.environ.get(
    'DIVERSITY_PUBLIC_KEY_PATH', root('../keys/diversity_dev_public.key')
)
DIVERSITY_PRIVATE_KEY_PATH = os.environ.get(
    'DIVERSITY_PRIVATE_KEY_PATH', root('../keys/diversity_dev_private.key')
)


# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
        'logstash': {
            '()': 'logstash_formatter.LogstashFormatter'
        }
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        }
    }
}

if 'RAVEN_CONFIG_DSN' in os.environ:
    RAVEN_CONFIG = {
        'dsn': os.environ.get('RAVEN_CONFIG_DSN'),
        'site': os.environ.get('RAVEN_CONFIG_SITE')
    }

    INSTALLED_APPS += (
        'raven.contrib.django.raven_compat',
    )

    MIDDLEWARE_CLASSES = (
        'raven.contrib.django.raven_compat.middleware.SentryResponseErrorIdMiddleware',
        #'raven.contrib.django.raven_compat.middleware.Sentry404CatchMiddleware',
    ) + MIDDLEWARE_CLASSES

# SECURITY

LOGIN_FAILURE_LIMIT = 5
LOGIN_FAILURE_COOLOFF_TIME = 60  # in minutes


# .local.py overrides all the common settings.
try:
    from .local import *
except ImportError:
    pass



# Django rest-framework-auth
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.OAuth2Authentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'core.permissions.AllowNone',
    ),
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    ),
    'DEFAULT_THROTTLE_RATES': {
        'login': '10/sec',
    }
}

# the start number of the LAA reference, must be 7 digit number and must
# not clash with existing - generated references so we are starting at 3million
LAA_REFERENCE_SEED = 3000000
TEST_MODE = False

STATSD_CLIENT = 'django_statsd.clients.normal'
STATSD_PREFIX = 'backend'

STATSD_PATCHES = [
    'django_statsd.patches.db',
]

STATSD_HOST = os.environ.get('STATSD_HOST', 'localhost')
STATSD_PORT = os.environ.get('STATSD_PORT', 8125)

if all([os.environ.get('SMTP_USER'),
        os.environ.get('SMTP_PASSWORD'),
        os.environ.get('SMTP_HOST')]):
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = os.environ.get('SMTP_HOST')
    EMAIL_HOST_USER = os.environ.get('SMTP_USER')
    EMAIL_HOST_PASSWORD = os.environ.get('SMTP_PASSWORD')
    EMAIL_PORT = 587
    EMAIL_USE_TLS = True
else:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

CALL_CENTRE_NOTIFY_EMAIL_ADDRESS = os.environ.get('CALL_CENTRE_NOTIFY_EMAIL_ADDRESS', 'ravi.kotecha@digital.justice.gov.uk')

PROVIDER_HOURS = {
    'weekday': (datetime.time(9, 0), datetime.time(17, 0))
}

OPERATOR_HOURS = {
    'weekday': (datetime.time(9, 0), datetime.time(20, 0)),
    'saturday': (datetime.time(9, 0), datetime.time(12, 30))
}


# importing test settings file if necessary (TODO chould be done better)
if len(sys.argv) > 1 and 'test' == sys.argv[1]:
    from .testing import *

