"""
SafeGuard AI — Testing Settings
Test run karne ke liye — fast, in-memory, Celery synchronous mode.
"""

from .base import *  # noqa: F401, F403

# ---------------------------------------------------------------------------
# Testing mode
# ---------------------------------------------------------------------------
DEBUG = True

# ---------------------------------------------------------------------------
# Database — in-memory SQLite for speed
# Tests ke baad automatically clean ho jata hai
# ---------------------------------------------------------------------------
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',  # RAM mein database — fastest option
    }
}

# ---------------------------------------------------------------------------
# Password Hashing — Tests mein fast hasher use karo (MD5 — only for tests!)
# ---------------------------------------------------------------------------
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# ---------------------------------------------------------------------------
# Celery — Tests mein synchronous mode (actual workers nahi chahiye)
# ---------------------------------------------------------------------------
CELERY_TASK_ALWAYS_EAGER = True          # Tasks turant execute honge
CELERY_TASK_EAGER_PROPAGATES = True      # Exceptions propagate honge
CELERY_BROKER_URL = 'memory://'          # In-memory broker

# ---------------------------------------------------------------------------
# Cache — Tests mein dummy cache
# ---------------------------------------------------------------------------
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

# ---------------------------------------------------------------------------
# Email — Tests mein locmem backend
# ---------------------------------------------------------------------------
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

# ---------------------------------------------------------------------------
# Media — Tests ke liye temp directory
# ---------------------------------------------------------------------------
import tempfile
MEDIA_ROOT = tempfile.mkdtemp()

# ---------------------------------------------------------------------------
# Logging — Tests mein quiet raho
# ---------------------------------------------------------------------------
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'CRITICAL',  # Sirf critical errors show karo
    },
}

# ---------------------------------------------------------------------------
# CORS — Tests mein allow all
# ---------------------------------------------------------------------------
CORS_ALLOW_ALL_ORIGINS = True

# ---------------------------------------------------------------------------
# Whitenoise — Tests mein disable
# ---------------------------------------------------------------------------
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'
