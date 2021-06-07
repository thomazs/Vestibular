from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'r3fg0=x5d$lpy3hb&l8n!a)s^hxa4a01+f$^ec%v^^itc76!!1'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['172.17.1.144', '127.0.0.1', 'localhost']

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'instituicao',
    'processo_seletivo',
    'django.contrib.humanize',
    'tinymce',
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

ROOT_URLCONF = 'Vestibular.urls'

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

WSGI_APPLICATION = 'Vestibular.wsgi.application'

# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }

if not os.getenv('USERDOMAIN') == 'DESKTOP-JO69D6U':
    PRODUCAO = True
    if PRODUCAO:
        DATABASES = {
            'default': {
                'ENGINE': 'mysql.connector.django',
                'NAME': 'uvest',
                'USER': 'root',
                'PASSWORD': '!WRUverse#2020!DB',
                'HOST': 'localhost',
            }
        }

# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = 'pt-br'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = False

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

# STATIC_ROOT = 'C:/xampp/htdocs/static'
STATIC_URL = '/static/'
# EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_USE_TLS = True
EMAIL_PORT = 587
EMAIL_HOST_USER = "alertas@uverse.com.vc"
EMAIL_HOST_PASSWORD = "AlertaFAAO2019!"

# HOST_CURRENT = 'http://localhost:8000'
HOST_CURRENT = 'http://uverse.in'

MEDIA_ROOT = os.path.join(BASE_DIR, 'processo_seletivo', 'static', 'media')
STATIC_ROOT = 'C:/xampp/htdocs/media'
MEDIA_URL = '/media/'
LOGIN_URL = '/uvest/admin/login'
LOGIN_REDIRECT_URL = '/uvest/admin/login'
FORCE_SCRIPT_NAME = '/uvest/'



TINYMCE_DEFAULT_CONFIG = {
    "plugins": "image", #plugins
}

TINYMCE_JS_URL = os.path.join("django-tinymce/tiny_mce.min.js")
TINYMCE_JS_ROOT = os.path.join("django-tinymce/tiny_mce")
