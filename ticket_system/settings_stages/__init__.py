"""
Django settings_stages for ticket_system project.

Staging is controlled via environment parameters:
    DJANGO_STAGE       DEV|TEST|PROD
    DJANGO_DEBUG       leave empty for production
    DJANGO_SECRET_KEY  the secret to be used
"""

import os

DJANGO_STAGE = os.environ.get('DJANGO_STAGE', 'DEV')
if DJANGO_STAGE.lower() not in ['dev', 'test', 'prod']:
    raise RuntimeError('Invalid DJANGO_STAGE "{}". Must be DEV|TEST|PROD'.format(DJANGO_STAGE))

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings_stages - unsuitable for production
# See https://docs.djangoproject.com/en/2.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'oyy(+&+vhe#xkfl3ypz3j2a4$1tn!le39ehy07nq1hxx@29y42')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = bool(os.environ.get('DJANGO_DEBUG', True)) or DJANGO_STAGE == 'DEV'

ALLOWED_HOSTS = []

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'booking.apps.BookingConfig',
    'closed_for_renovation.apps.ClosedForRenovationConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'ticket_system.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')]
        ,
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'ticket_system.wsgi.application'

# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'DATABASE_NAME',
        'USER': 'DATABASE_USER',
        'PASSWORD': 'DATABASE_PASSWORD',
        'HOST': 'DATABASE_HOST',
        'PORT': 1234,
        'OPTIONS': {
        }
    }
}

# Password validation
# https://docs.djangoproject.com/en/2.0/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/2.0/topics/i18n/

LANGUAGE_CODE = 'de_DE'
TIME_ZONE = 'Europe/Berlin'
USE_I18N = True
USE_L10N = True
USE_TZ = True

DATE_FORMAT = "l, j. F Y"
TIME_FORMAT = "G:i"
# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.0/howto/static-files/

STATIC_URL = '/static/'

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'EMAIL_HOST'
EMAIL_PORT = 1025

if DJANGO_STAGE.lower() == "dev":
    from .local import *
elif DJANGO_STAGE.lower() == 'test':
    from .test import *
elif DJANGO_STAGE.lower() == 'prod':
    from .production import *
