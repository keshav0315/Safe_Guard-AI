"""
SafeGuard AI — Base Django Settings
Yahan saare common settings hain jo sabhi environments mein use honge.
"""

import os
from pathlib import Path
from datetime import timedelta
import environ

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
# BASE_DIR → safeguard_backend/  (ye directory hai jahan ye file exist karti hai ke parent)
# Backend root → manage.py wali directory
BASE_DIR = Path(__file__).resolve().parent.parent.parent  # safeguard_backend/
BACKEND_ROOT = BASE_DIR.parent  # backend/

# ---------------------------------------------------------------------------
# django-environ setup
# ---------------------------------------------------------------------------
env = environ.Env(
    DEBUG=(bool, False),
    ALLOWED_HOSTS=(list, []),
)

# .env file backend root mein hona chahiye
environ.Env.read_env(BACKEND_ROOT / '.env')

# ---------------------------------------------------------------------------
# Security
# ---------------------------------------------------------------------------
SECRET_KEY = env('DJANGO_SECRET_KEY')

DEBUG = env('DJANGO_DEBUG', default=False)

ALLOWED_HOSTS = env.list('DJANGO_ALLOWED_HOSTS', default=[])

# ---------------------------------------------------------------------------
# Application definition
# ---------------------------------------------------------------------------
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

THIRD_PARTY_APPS = [
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'corsheaders',
    'drf_spectacular',
]

LOCAL_APPS = [
    # Yeh saare apps safeguard_backend/apps/ mein hain
    'apps.users',
    'apps.contacts',
    'apps.emergencies',
    'apps.locations',
    'apps.notifications',
    'apps.ai_detection',
    'apps.audit',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# ---------------------------------------------------------------------------
# Custom User Model
# ---------------------------------------------------------------------------
AUTH_USER_MODEL = 'users.User'

# ---------------------------------------------------------------------------
# Middleware
# ---------------------------------------------------------------------------
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',       # Static files ke liye
    'corsheaders.middleware.CorsMiddleware',             # CORS headers
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

WSGI_APPLICATION = 'config.wsgi.application'
ASGI_APPLICATION = 'config.asgi.application'

# ---------------------------------------------------------------------------
# Database — PostgreSQL (env vars se configure hoga)
# ---------------------------------------------------------------------------
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env('DB_NAME', default='safeguard_db'),
        'USER': env('DB_USER', default='safeguard_user'),
        'PASSWORD': env('DB_PASSWORD', default=''),
        'HOST': env('DB_HOST', default='localhost'),
        'PORT': env('DB_PORT', default='5432'),
        'OPTIONS': {
            'connect_timeout': 10,
        },
        'CONN_MAX_AGE': 60,  # Connection pooling — 60 seconds tak connection open rakho
    }
}

# ---------------------------------------------------------------------------
# Password Validators
# ---------------------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ---------------------------------------------------------------------------
# Internationalisation
# ---------------------------------------------------------------------------
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'   # IST — Indian Standard Time
USE_I18N = True
USE_TZ = True

# ---------------------------------------------------------------------------
# Static & Media Files
# ---------------------------------------------------------------------------
STATIC_URL = '/static/'
STATIC_ROOT = BACKEND_ROOT / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BACKEND_ROOT / 'media'

# WhiteNoise ke liye compressed static files
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# ---------------------------------------------------------------------------
# Default Primary Key
# ---------------------------------------------------------------------------
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ---------------------------------------------------------------------------
# Django REST Framework
# ---------------------------------------------------------------------------
REST_FRAMEWORK = {
    # JWT authentication by default — har request mein token check hoga
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    ),
    'DEFAULT_PARSER_CLASSES': (
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.MultiPartParser',
        'rest_framework.parsers.FormParser',
    ),
    # Pagination — ek baar mein 20 results
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    # Schema generation ke liye drf-spectacular
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    # Throttling — rate limiting
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour',
    },
    # Exception handling
    'EXCEPTION_HANDLER': 'common.exceptions.handlers.custom_exception_handler',
}

# ---------------------------------------------------------------------------
# Simple JWT Settings
# ---------------------------------------------------------------------------
SIMPLE_JWT = {
    # Access token — 60 minutes valid rahega
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    # Refresh token — 7 din valid rahega
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,         # Naya refresh token dena baar use ke baad
    'BLACKLIST_AFTER_ROTATION': True,      # Purana token blacklist karo
    'UPDATE_LAST_LOGIN': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'TOKEN_OBTAIN_SERIALIZER': 'rest_framework_simplejwt.serializers.TokenObtainPairSerializer',
    'TOKEN_REFRESH_SERIALIZER': 'rest_framework_simplejwt.serializers.TokenRefreshSerializer',
}

# ---------------------------------------------------------------------------
# DRF Spectacular (OpenAPI / Swagger)
# ---------------------------------------------------------------------------
SPECTACULAR_SETTINGS = {
    'TITLE': 'SafeGuard AI API',
    'DESCRIPTION': (
        'SafeGuard AI — Women Safety Application API. '
        'Yeh API emergency alerts, location tracking, aur AI-based threat detection provide karta hai.'
    ),
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'SCHEMA_PATH_PREFIX': '/api/v1/',
    'COMPONENT_SPLIT_REQUEST': True,
    'SORT_OPERATIONS': False,
    'TAGS': [
        {'name': 'Auth', 'description': 'Authentication endpoints — login, register, token refresh'},
        {'name': 'Users', 'description': 'User profile management'},
        {'name': 'Contacts', 'description': 'Emergency contacts management'},
        {'name': 'Emergencies', 'description': 'Emergency alerts and SOS'},
        {'name': 'Locations', 'description': 'Location tracking and history'},
        {'name': 'Notifications', 'description': 'Push notifications'},
        {'name': 'AI Detection', 'description': 'AI-based threat detection'},
        {'name': 'Audit', 'description': 'Audit logs'},
    ],
}

# ---------------------------------------------------------------------------
# CORS Settings
# ---------------------------------------------------------------------------
CORS_ALLOWED_ORIGINS = env.list('CORS_ALLOWED_ORIGINS', default=[
    'http://localhost:3000',
    'http://127.0.0.1:3000',
])
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
    'x-request-id',
]

# ---------------------------------------------------------------------------
# Celery Settings (Redis as broker)
# ---------------------------------------------------------------------------
CELERY_BROKER_URL = env('CELERY_BROKER_URL', default='redis://localhost:6379/1')
CELERY_RESULT_BACKEND = env('CELERY_RESULT_BACKEND', default='redis://localhost:6379/2')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60   # 30 minutes max task time
CELERY_TASK_SOFT_TIME_LIMIT = 25 * 60  # Soft limit — warning bhejega
# Beat schedule ke liye
CELERY_BEAT_SCHEDULE = {}

# ---------------------------------------------------------------------------
# Redis Cache
# ---------------------------------------------------------------------------
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': env('REDIS_URL', default='redis://localhost:6379/0'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'IGNORE_EXCEPTIONS': True,  # Redis down hone pe gracefully handle karo
        },
        'KEY_PREFIX': 'safeguard',
        'TIMEOUT': 300,  # 5 minutes default cache timeout
    }
}

# ---------------------------------------------------------------------------
# Firebase Settings
# ---------------------------------------------------------------------------
FIREBASE_CREDENTIALS_PATH = env('FIREBASE_CREDENTIALS_PATH', default='')
FIREBASE_PROJECT_ID = env('FIREBASE_PROJECT_ID', default='')

# ---------------------------------------------------------------------------
# Email (override in environment-specific settings)
# ---------------------------------------------------------------------------
DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL', default='noreply@safeguard.ai')
SERVER_EMAIL = env('SERVER_EMAIL', default='server@safeguard.ai')

# ---------------------------------------------------------------------------
# Sentry Error Tracking (optional)
# ---------------------------------------------------------------------------
SENTRY_DSN = env('SENTRY_DSN', default='')

if SENTRY_DSN:
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration
    from sentry_sdk.integrations.celery import CeleryIntegration
    from sentry_sdk.integrations.redis import RedisIntegration

    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[
            DjangoIntegration(transaction_style='url'),
            CeleryIntegration(),
            RedisIntegration(),
        ],
        traces_sample_rate=0.1,  # 10% transactions ko trace karo
        send_default_pii=False,   # PII data mat bhejo
        environment=env('DJANGO_ENVIRONMENT', default='production'),
    )

# ---------------------------------------------------------------------------
# Logging Configuration (structlog-compatible)
# ---------------------------------------------------------------------------
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
        # JSON formatter structlog ke liye
        'json': {
            '()': 'structlog.stdlib.ProcessorFormatter',
            'processors': [
                'structlog.stdlib.ProcessorFormatter.wrap_for_formatter',
            ],
        },
    },
    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['console', 'mail_admins'],
            'level': 'ERROR',
            'propagate': False,
        },
        'django.security': {
            'handlers': ['console'],
            'level': 'WARNING',
            'propagate': False,
        },
        # SafeGuard AI app-specific loggers
        'apps': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'celery': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
