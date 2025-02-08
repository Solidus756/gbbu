import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

# Chargement des variables d'environnement
load_dotenv(dotenv_path=BASE_DIR / ".env")

SECRET_KEY = os.getenv('SECRET_KEY', 'change-me-secret-key')
DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'gb.intradc.ovh', '192.168.0.19']

# Applications installées, incluant Django JET et nos apps
INSTALLED_APPS = [
    'jet',
    'jet.dashboard',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'accounts',
    'twitch',
    'notifications',
    'acl',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
]

ROOT_URLCONF = 'charity_streaming.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # Pour simplifier, on suppose que les templates sont placés dans chaque app ou dans un dossier global "templates"
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.static',
            ],
        },
    },
]

WSGI_APPLICATION = 'charity_streaming.wsgi.application'
ASGI_APPLICATION = 'charity_streaming.asgi.application'

# Configuration de la base de données (exemple PostgreSQL)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'busterevent',
        'USER': 'busters',
        'PASSWORD': os.getenv('DB_PASSWORD', 'changeme'),
        'HOST': 'localhost',
        'PORT': '',
    }
}

# Internationalisation
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Fichiers statiques et médias
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'static_collected'
STATICFILES_DIRS = [BASE_DIR / 'static']

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Configuration SMTP personnalisée (pour envoi d'emails)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'  # en dev, à changer en prod

# Paramètres Twitch (doivent être définis dans le fichier .env)
TWITCH_CLIENT_ID = os.getenv("TWITCH_CLIENT_ID", "")
TWITCH_SECRET = os.getenv("TWITCH_SECRET", "")
