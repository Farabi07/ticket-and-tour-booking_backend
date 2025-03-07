"""
Django settings for start_project project.

Generated by 'django-admin startproject' using Django 4.0.3.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.0/ref/settings/
"""

import os
from datetime import timedelta
from pathlib import Path


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-u-e(&(%d#(e+gj+nel$(-gefvmg$uwr9v747d7c8^&hqo8amh@'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = [
    '*'
]

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # 3rd party
    'rest_framework',
    'corsheaders',
    'drf_spectacular',
    'phonenumber_field',
    'djoser',
    'django_filters',


    # local
    'account.apps.AccountConfig',
    'authentication.apps.AuthenticationConfig',
    'member.apps.MemberConfig',
    'tour.apps.TourConfig',
    'donation.apps.DonationConfig',
    'site_settings.apps.SiteSettingsConfig',
    'support.apps.SupportConfig',
    'donation_report.apps.DonationReportConfig',
    'bbms',
    'payments',
    'cms.apps.CmsConfig',
    'dashboard'
]

INSTALLED_APPS += ['sequences.apps.SequencesConfig']

MIDDLEWARE = [
    # Simplified static file serving.
    # https://warehouse.python.org/project/whitenoise/
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_currentuser.middleware.ThreadLocalUserMiddleware',
    # 'silk.middleware.SilkyMiddleware',
]
DJANGO_SETTINGS_MODULE = 'start_project.settings' 
ROOT_URLCONF = 'start_project.urls'


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'start_project.wsgi.application'


AUTH_USER_MODEL = 'authentication.User'

AUTHENTICATION_BACKENDS = [
    'authentication.backends.EmailorPhoneModelBackend'
]


STRIPE_PUBLIC_KEY ='pk_test_51QvcVcH5cscgBQuXnttFXi0clmPxZZqTQXW8GglPJFHSoOw59eSJYhguuPw6vvFsxx7Sti0CLDiLKkOJoeKn7Bi9002MxBwL47'
STRIPE_SECRET_KEY ='sk_test_51QvcVcH5cscgBQuX8zA1qfjlHdV74WO5QWgS70tEVVmtgtw2SNAtt5kYagv3guYBMbYekplXkzUZLrKYmE2NGqCh00jkshVcUv'
# STRIPE_ENDPOINT_SECRET='whsec_2991f9a5bf0fa25f0c230e10a1e4a7b3358ee861f8fd5ff56d274310400b64d2'
STRIPE_ENDPOINT_SECRET ='whsec_2991f9a5bf0fa25f0c230e10a1e4a7b3358ee861f8fd5ff56d274310400b64d2'
# STRIPE_PUBLIC_KEY = " pk_test_51QrXBcCePADtqSXePxavF9aPax1UFP8XQqtCpU62anlI4zNsQXxwXM7LZWjVabhwSQZUNROVygiKWaK8iLrs5Qtb00NKVq5Z4Y"
# STRIPE_SECRET_KEY = "sk_test_51QrXBcCePADtqSXeJt3PkbgNCepKow6NMTSguFfr8ZFzMUgeoCdsAVw6KlhahJ1WhupUougqi34BNfps4Ec0MPgp00iD7d8C8e"
# STRIPE_ENDPOINT_SECRET = 'whsec_vcFsMk7RnP3uBm9MgUwoS3XUJceyU5et'
# STRIPE_ENDPOINT_SECRET = 'whsec_2991f9a5bf0fa25f0c230e10a1e4a7b3358ee861f8fd5ff56d274310400b64d2'
import os
from dotenv import load_dotenv

# load_dotenv()

# STRIPE_PUBLIC_KEY = os.getenv('STRIPE_PUBLIC_KEY')
# STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY')
# STRIPE_ENDPOINT_SECRET = os.getenv('STRIPE_ENDPOINT_SECRET')

# # Use the appropriate keys based on the environment
# if os.getenv('DJANGO_ENV') == 'production':
#     STRIPE_PUBLIC_KEY = os.getenv('STRIPE_PUBLIC_KEY_PROD')
#     STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY_PROD')
#     STRIPE_ENDPOINT_SECRET = os.getenv('STRIPE_ENDPOINT_SECRET_PROD')
# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',  # Saves the database file in your project directory
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Dhaka'

USE_I18N = True

USE_L10N = True

USE_TZ = True

WHITENOISE_USE_FINDERS = True
CORS_ALLOW_ALL_ORIGINS = True

CORS_ALLOWED_ORIGINS = [
    # '*'
    # https://bustours.dreamtourism.co.uk/
    # "http://127.0.0.1:3000",
    # "https://example.com",
    # "https://sub.example.com",
    # "http://localhost:8080",
]

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/

STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')  # media files upload directory
MEDIA_URL = '/media/'  # media files retrieve directory

# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = 'smtp.gmail.com'
# EMAIL_PORT = 587
# EMAIL_HOST_USER = 'cashconnecdev1@gmail.com'
# EMAIL_HOST_PASSWORD = 'CashConnect@2021'
# EMAIL_USE_TLS = True
# DEFAULT_FROM_EMAIL = 'admin@bluebayit.com'



# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST='smtp.titan.email'
# EMAIL_PORT= 587
# EMAIL_HOST_USER= "sales@dreamtourism.it"
# EMAIL_HOST_PASSWORD = 'Dream@2023'
# EMAIL_USE_TLS = True

# ADMIN_EMAIL = "sales@dreamtourism.it"
# SUPPORT_EMAIL = "sales@dreamtourism.it"
# DEFAULT_FROM_EMAIL = ADMIN_EMAIL
# SERVER_EMAIL = ADMIN_EMAIL

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST='smtp.titan.email'
EMAIL_PORT= 587
EMAIL_HOST_USER= "sales@dreamtourism.co.uk"
EMAIL_HOST_PASSWORD = 'Dream@2023~'
EMAIL_USE_TLS = True

ADMIN_EMAIL = "sales@dreamtourism.co.uk"
SUPPORT_EMAIL = "sales@dreamtourism.co.uk"
DEFAULT_FROM_EMAIL = ADMIN_EMAIL
SERVER_EMAIL = ADMIN_EMAIL
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST='smtp.titan.email'
# EMAIL_PORT= 587
# EMAIL_HOST_USER= "sales@dreamziarah.com"
# EMAIL_HOST_PASSWORD = 'Dream@2023~'
# EMAIL_USE_TLS = True

# ADMIN_EMAIL = "sales@dreamziarah.com"
# SUPPORT_EMAIL = "sales@dreamziarah.com"
# DEFAULT_FROM_EMAIL = ADMIN_EMAIL
# SERVER_EMAIL = ADMIN_EMAIL

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.MultiPartParser',
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.FormParser',
    ],
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
    ),
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'Dream Tour Booking UK API',
    'DESCRIPTION': '',
    'VERSION': '1.0.0',
    # OTHER SETTINGS
    # available SwaggerUI configuration parameters
    # https://swagger.io/docs/open-source-tools/swagger-ui/usage/configuration/
    "SWAGGER_UI_SETTINGS": {
        "deepLinking": True,
        "persistAuthorization": True,
        # "displayOperationId": True,
    },
    # available SwaggerUI versions: https://github.com/swagger-api/swagger-ui/releases
    "SWAGGER_UI_DIST": "//unpkg.com/swagger-ui-dist@3.35.1",  # default
    # "SWAGGER_UI_FAVICON_HREF": STATIC_URL + "your_company_favicon.png", # default is swagger favicon
    # "APPEND_COMPONENTS": {
    # "securitySchemes": {
    # 		"ApiKeyAuth": {
    # 				"type": "apiKey",
    # 				"in": "header",
    # 				"name": "Authorization"
    # 		}
    # 	}
    # },
    # "SECURITY": [{"ApiKeyAuth": [], }],
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=30),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,

    'ALGORITHM': 'HS256',
    # 'SIGNING_KEY': settings.SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': None,

    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'USER_AUTHENTICATION_RULE': 'rest_framework_simplejwt.authentication.default_user_authentication_rule',

    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',

    'JTI_CLAIM': 'jti',

    'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
    'SLIDING_TOKEN_LIFETIME': timedelta(minutes=5),
    'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=1),
}

DJOSER = {

    'LOGIN_FIELD': 'email',
    'USER_CREATE_PASSWORD_RETYPE': True,
    'USERNAME_CHANGED_EMAIL_CONFIRMATION': True,
    'PASSWORD_CHANGED_EMAIL_CONFIRMATION': True,
    'SEND_CONFIRMATION_EMAIL': True,
    'SET_USERNAME_RETYPE': True,
    'SET_PASSWORD_RETYPE': True,
    'PASSWORD_RESET_CONFIRM_URL': 'password/reset/confirm/{uid}/{token}',
    'USERNAME_RESET_CONFIRM_URL': 'email/reset/confirm/{uid}/{token}',
    'ACTIVATION_URL': 'activate/{uid}/{token}',
    'SEND_ACTIVATION_EMAIL': True,
    'SERIALIZERS': {
        'user_create': 'authentication.serializers.UserSerializer',
        'user': 'authentication.serializers.UserSerializer',
        'current_user': 'authentication.serializers.UserSerializer',
        'user_delete': 'djoser.  .UserDeleteSerializer',
    }
}
