import os
from pathlib import Path
from dotenv import load_dotenv

# Répertoire de base du projet
BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'change-me-secret-key'
DEBUG = True

ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '192.168.0.19',  # Ajoutez ici l'IP/domaine nécessaire
    'gb.intradc.ovh',
]


CSRF_TRUSTED_ORIGINS = [
    'https://gb.intradc.ovh',  # Ajoutez votre domaine ici
]

# Indiquez à Django de respecter l'en-tête HTTP X-Forwarded-Proto envoyé par HAProxy
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
'''
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
        'django.core.mail': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}
'''
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Applications installées
INSTALLED_APPS = [
    'jet.dashboard',
    'jet',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'widget_tweaks',
    
    # Apps du projet
    'main_app.apps.MainAppConfig',
]

MIDDLEWARE = [
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
]

ROOT_URLCONF = 'charity_streaming.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],  # On compte sur APP_DIRS=True pour trouver les templates dans main_app/templates
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.static',
                'main_app.views.notifications_context',  # ✅ Ajout du contexte notifications
                'main_app.context_processors.notification_context',  # ✅ Ajout du context processor
            ],
        },
    },
]

# Activer le debug des templates
#TEMPLATES[0]['OPTIONS']['debug'] = True

WSGI_APPLICATION = 'charity_streaming.wsgi.application'
ASGI_APPLICATION = 'charity_streaming.asgi.application'

# Base de données PostgreSQL (exemple)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'charity_streaming',
        'USER': 'charity_streaming',
        'PASSWORD': 'hpGB52Sna57A8c',
        'HOST': 'localhost',
        'PORT': '',
    }
}

# Internationalisation
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Fichiers statiques
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'static_collected'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

load_dotenv(dotenv_path=BASE_DIR / ".env")  # charge les variables depuis le fichier .env

TWITCH_CLIENT_ID = os.getenv("TWITCH_CLIENT_ID", "")
TWITCH_SECRET = os.getenv("TWITCH_SECRET", "")

# 2FA (exemple minimal, à compléter si vous utilisez django-two-factor-auth)
