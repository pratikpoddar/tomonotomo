# Django settings for tomonotomo_project project.

DEBUG = True
TEMPLATE_DEBUG = True
 
DEBUG = False
TEMPLATE_DEBUG = False

ADMINS = (
    ('Pratik Poddar', 'pratik.phodu@gmail.com'),
)

MANAGERS = ADMINS

#EMAIL_USE_TLS = True
#EMAIL_HOST = 'smtp.gmail.com'
#EMAIL_PORT = 587
#EMAIL_HOST_USER = 'pratik.phodu@gmail.com'
#EMAIL_HOST_PASSWORD = 'indiarocks'
#DEFAULT_FROM_EMAIL = 'pratik.phodu@gmail.com'
#SERVER_EMAIL = 'pratik.phodu@gmail.com'

FAILED_RUNS_CRONJOB_EMAIL_PREFIX = "[Django - Tomonotomo - Cron Job] "
EMAIL_SUBJECT_PREFIX = "[Django - Tomonotomo] "

#DATABASES = {
#    'default': {
#        'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
#        'NAME': '/home/himangshu/pratik/databasefile',                      # Or path to database file if using sqlite3.
#        # The following settings are not used with sqlite3:
#        'USER': '',
#        'PASSWORD': '',
#        'HOST': '',                      # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
#        'PORT': '',                      # Set to empty string for default.
#    }
#}

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'tomonotomo_db',
        'USER': 'tomonotomo_user',
        'PASSWORD': '12345678',
        'HOST': 'localhost',
        'PORT': '', # Set to empty string for default.
    }
}

SESSION_COOKIE_DOMAIN = '.tomonotomo.com'
CSRF_COOKIE_DOMAIN = None
# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
ALLOWED_HOSTS = ['tomonotomo.com','www.tomonotomo.com']

USE_X_FORWARDED_HOST = True

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'America/Chicago'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/var/www/example.com/media/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://example.com/media/", "http://media.example.com/"
MEDIA_URL = ''

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/var/www/example.com/static/"
STATIC_ROOT = ''

# URL prefix for static files.
# Example: "http://example.com/static/", "http://static.example.com/"
STATIC_URL = '/static/'

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
    'compressor.finders.CompressorFinder'
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = ')-14#5qt%6t0saupl^8_$j!8*rgj(!pq#=hof#khz*mnqcm_3j'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.request',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # 'django.middleware.common.BrokenLinkEmailsMiddleware'
    'tomonotomo_project.middleware.error500Middleware',
    'tomonotomo_project.minidetector.Middleware'
)

ROOT_URLCONF = 'tomonotomo_project.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'tomonotomo_project.wsgi.application'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Uncomment the next line to enable the admin:
    'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
    'meta',
    'tomonotomo',
    'social_auth',
    'functools32',
    'django_cron',
    'south',
    'compressor'
)

LOG_DIR='/home/ubuntu/django_log'
COMPRESS_ROOT = '/home/ubuntu/tomonotomo/tomonotomo/static/'

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '[%(name)s]- %(levelname)s- %(asctime)s '
                      ' %(filename)s: %(lineno)d - %(message)s',
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler',
            'formatter': 'standard',
        },
        'file_debug': {
            'level': 'DEBUG',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'formatter': 'standard',
            'filename': LOG_DIR + "/debug.log",
        },
        'file_error': {
            'level': 'ERROR',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'formatter': 'standard',
            'filename': LOG_DIR + "/error.log",
        }
    },
    'loggers': {
        '': {
            'handlers': ['file_debug', 'file_error', 'mail_admins'],
            'level': 'DEBUG',
            'propagate': True,
        },
    }
}

CRON_CLASSES = [
    "tomonotomo.social_auth_pipeline.startPostProcessing",
    "tomonotomo.social_auth_pipeline.updateQuota",
]

FACEBOOK_APP_ID='1398031667088132'
FACEBOOK_API_SECRET='c264a27d591710a5bfbf072043623dbd'

AUTHENTICATION_BACKENDS = (
    'social_auth.backends.facebook.FacebookBackend',
    'django.contrib.auth.backends.ModelBackend',
)

FACEBOOK_EXTENDED_PERMISSIONS= ['email', 'user_birthday', 'user_relationships', 'friends_relationships', 'friends_birthday', 'friends_education_history', 'friends_work_history', 'friends_hometown', 'friends_location', 'user_likes', 'friends_likes']

SOCIAL_AUTH_PIPELINE = (
    'social_auth.backends.pipeline.social.social_auth_user',
    'social_auth.backends.pipeline.associate.associate_by_email',
    'social_auth.backends.pipeline.user.get_username',
    'social_auth.backends.pipeline.user.create_user',    

    'tomonotomo.social_auth_pipeline.create_custom_user',
   
    'social_auth.backends.pipeline.social.associate_user',
    'social_auth.backends.pipeline.user.update_user_details',
)

SOCIAL_AUTH_CREATE_USERS = True
SOCIAL_AUTH_FORCE_RANDOM_USERNAME = False
SOCIAL_AUTH_DEFAULT_USERNAME = 'socialauth_user'
SOCIAL_AUTH_ENABLED_BACKENDS = ('facebook',)
SOCIAL_AUTH_COMPLETE_URL_NAME = 'socialauth_complete'
SOCIAL_AUTH_ASSOCIATE_URL_NAME = 'socialauth_associate_complete'
SOCIAL_AUTH_ASSOCIATE_BY_EMAIL = True
SOCIAL_AUTH_ERROR_KEY = 'socialauth_error'
SOCIAL_AUTH_REDIRECT_IS_HTTPS = False

LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/loggedin'
LOGIN_ERROR_URL = '/loginerror'


META_SITE_PROTOCOL = 'https'

