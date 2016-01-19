"""
Django settings for web project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'suqzb*2w1u#%k67vmp=%x70pf4(pua6#1*f$%s(s^3gr*@!10g'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
    #'django.contrib.admin',
    #'django.contrib.auth',
    #'django.contrib.contenttypes',
    #'django.contrib.sessions',
    #'django.contrib.messages',
    'django.contrib.staticfiles',
    'jstemplate',
    'web.zoo',
    'web.zooapi',
    'web.taskqueue',
)

MIDDLEWARE_CLASSES = (
    'web.zoo.middleware.StaticFilesCachingMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    # 'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'web.urls'

WSGI_APPLICATION = 'web.wsgi.application'

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = False
USE_L10N = False
USE_TZ = False
STATIC_URL = '/static/'
JSTEMPLATE_EXTS = ('hbs',)


from core.settings import Settings
zoo_settings = Settings.get_instance()

if not zoo_settings:
    raise RuntimeError('No zoo settings')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(zoo_settings.storage_path, 'db.sqlite3'),
    }
}



