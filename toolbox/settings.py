import os,sys
# Django settings for toolbox project.

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ROOT=os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(ROOT)

ADMINS = (
    ('Theo', 'tkleinen@gmail.com'),
)

MANAGERS = ADMINS

AUTH_PROFILE_MODULE = "toolbox.UserProfile"
LOGIN_REDIRECT_URL = "/"
LOGOUT_URL = "/"

DATABASES = {
    'default': {
        'ENGINE': 'mysql',
        'NAME': 'toolbox',
        'USER': 'acacia',
        'PASSWORD': 'Beaumont1',
        'HOST': 'db',
        'PORT': '3306',
    }
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/Amsterdam'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'nl-nl'
LANGUAGES = (
    ('nl', 'Nederlands'),
    ('en', 'English'),
)

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
# c:/src/toolbox/uploads
MEDIA_ROOT = os.path.abspath(os.path.join(ROOT, 'media'))

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
# c:/src/toolbox/static
STATIC_ROOT = os.path.abspath(os.path.join(ROOT, 'static'))

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# URL prefix for admin static files -- CSS, JavaScript and images.
# Make sure to use a trailing slash.
# Examples: "http://foo.com/static/admin/", "/static/admin/".
ADMIN_MEDIA_PREFIX = '/static/admin/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'k0b6tc#pw5amhvax#jg%@uv#)a&-sjjaaf^&f+jj((-ux#wyob'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

ROOT_URLCONF = 'toolbox.urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.abspath(os.path.join(ROOT, 'templates')),
    '/usr/local/lib/python2.7/dist-packages/categories/editor/templates'
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'django.contrib.admindocs',
    'django.contrib.gis',
    'django.contrib.humanize',  
    'categories',
    'categories.editor',
    'registration',
    'mptt',
#     'south',
    'olwidget',
    'toolbox',
    'analytical', 
)


# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

CATEGORIES_SETTINGS = {
    'FK_REGISTRY': {
        'toolbox.Problem': 'category'
    }
}

GEOS_LIBRARY_PATH = '/usr/lib/libgeos_c.so'
GOOGLE_MAPS_API_KEY = 'ABQIAAAAxcqUzT4EjBrFXX3u1aMLFxT2yXp_ZAY8_ufC3CFXhHIE1NvwkxSa8ll5ork4FXojYjOZ2rW7db8Xnw'
OL_API = 'http://openlayers.org/api/2.12/OpenLayers.js'
GOOGLE_ANALYTICS_PROPERTY_ID = 'UA-38298164-1'
GOOGLE_ANALYTICS_TRACKING_STYLE = 1
ANALYTICAL_AUTO_IDENTIFY = True
#ANALYTICAL_INTERNAL_IPS=['192.168.1.70',]

OLWIDGET_DEFAULT_OPTIONS = {
    'default_lat': 52,
    'default_lon': 5,
    'default_zoom': 8,
    'layers': ['osm.mapnik', 'google.streets', 'google.physical', 'google.satellite', 'google.hybrid', 
               #'osm.map', 'osm.mapnik', 'osm.osmarender',
               #'yahoo.map', 'yahoo.satellite', 'yahoo.hybrid',
               #'ve.road', 've.shaded', 've.aerial', 've.hybrid',
               #'wms.map', 'wms.nasa', 'wms.blank'
               ],
}

# registration stuff
ACCOUNT_ACTIVATION_DAYS=7
#EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
EMAIL_HOST='smtp.gmail.com'
EMAIL_PORT=587
EMAIL_HOST_USER='grondwatertoolbox@gmail.com'
EMAIL_HOST_PASSWORD='pw4toolbox'
EMAIL_USE_TLS = True
# end of registration stuff
