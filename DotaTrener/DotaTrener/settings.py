# DotaTrener/settings.py
import os
from pathlib import Path
from dotenv import load_dotenv

# 1️⃣ Загружаем .env ДО всех остальных настроек
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# 2️⃣ Базовые настройки Django
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'django-insecure-fallback-for-dev-only')
DEBUG = os.getenv('DJANGO_DEBUG', 'True').lower() == 'true'
ALLOWED_HOSTS = os.getenv('DJANGO_ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Сторонние приложения
    'rest_framework',
    'rest_framework.authtoken',
    'django_filters',
    'corsheaders',
    # Ваши приложения
    'coaching',
    'stratz_meta',
]
CORS_ALLOW_ALL_ORIGINS = True
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:8081")
MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",  
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'DotaTrener.urls'
WSGI_APPLICATION = 'DotaTrener.wsgi.application'

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

#  PostgreSQL конфигурация (читает из .env)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME', 'dotatrener_db'),
        'USER': os.getenv('DB_USER', 'DotaTrener_user'),
        'PASSWORD': os.getenv('DB_PASSWORD', '1234'),
        'HOST': os.getenv('DB_HOST', '127.0.0.1'),
        'PORT': os.getenv('DB_PORT', '5432'),
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'ru-RU'
TIME_ZONE = 'Europe/Moscow'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# 3️⃣ Настройки Django REST Framework
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour',
    },
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
    ],
}

# 4️⃣ Внешние API (Stratz)
STRATZ_API_KEY = os.getenv('STRATZ_API_KEY', '')
STRATZ_API_URL = os.getenv('STRATZ_API_URL', 'https://api.stratz.com/graphql')
STRATZ_REST_URL = os.getenv('STRATZ_REST_URL', 'https://api.stratz.com/api/v1')
STRATZ_PATCH_VERSION = os.getenv('STRATZ_PATCH_VERSION', '7.38')
STRATZ_REQUEST_DELAY = float(os.getenv('STRATZ_REQUEST_DELAY', '0.4'))
STRATZ_BUILDS_TAKE = int(os.getenv('STRATZ_BUILDS_TAKE', '100'))
# Для оценки GPM/XPM, когда Stratz не отдаёт goldPerMinute (делим networth/xp на минуты)
STRATZ_AVG_MATCH_MINUTES = float(os.getenv('STRATZ_AVG_MATCH_MINUTES', '35'))