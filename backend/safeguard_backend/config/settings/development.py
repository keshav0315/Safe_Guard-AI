"""
SafeGuard AI — Development Settings
Local development ke liye — debug on, SQLite allowed, CORS sab allow karo.
"""

from .base import *  # noqa: F401, F403
import environ

env = environ.Env()

# ---------------------------------------------------------------------------
# Debug Mode — development mein ON
# ---------------------------------------------------------------------------
DEBUG = True

ALLOWED_HOSTS = ['*']

# ---------------------------------------------------------------------------
# Database — development mein PostgreSQL ya SQLite use kar sakte ho
# USE_SQLITE=True set karo .env mein SQLite ke liye
# ---------------------------------------------------------------------------
USE_SQLITE = env.bool('USE_SQLITE', default=False)

if USE_SQLITE:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BACKEND_ROOT / 'db.sqlite3',  # noqa: F405
        }
    }

# ---------------------------------------------------------------------------
# CORS — development mein sab kuch allow karo
# ---------------------------------------------------------------------------
CORS_ALLOW_ALL_ORIGINS = True

# ---------------------------------------------------------------------------
# Email — console mein print karo (actual email mat bhejo)
# ---------------------------------------------------------------------------
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# ---------------------------------------------------------------------------
# Django Debug Toolbar (optional — agar installed hai)
# ---------------------------------------------------------------------------
try:
    import debug_toolbar  # noqa: F401
    INSTALLED_APPS += ['debug_toolbar']  # noqa: F405
    MIDDLEWARE = ['debug_toolbar.middleware.DebugToolbarMiddleware'] + MIDDLEWARE  # noqa: F405
    INTERNAL_IPS = ['127.0.0.1']
    DEBUG_TOOLBAR_CONFIG = {
        'SHOW_TOOLBAR_CALLBACK': lambda request: DEBUG,
    }
except ImportError:
    pass  # debug_toolbar installed nahi — koi baat nahi

# ---------------------------------------------------------------------------
# Cache — development mein simple in-memory cache
# ---------------------------------------------------------------------------
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'safeguard-dev-cache',
    }
}

# ---------------------------------------------------------------------------
# Logging — development mein verbose logging
# ---------------------------------------------------------------------------
LOGGING['loggers']['apps']['level'] = 'DEBUG'  # noqa: F405

# ---------------------------------------------------------------------------
# JWT — development mein longer expiry for convenience
# ---------------------------------------------------------------------------
from datetime import timedelta
SIMPLE_JWT = {  # noqa: F405
    **SIMPLE_JWT,  # noqa: F405
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=24),   # Dev mein 24 ghante
    'REFRESH_TOKEN_LIFETIME': timedelta(days=30),   # Dev mein 30 din
}

# ---------------------------------------------------------------------------
# Media files dev server se serve karo
# ---------------------------------------------------------------------------
# (Django dev server automatically media serve karta hai urls.py mein setup ke saath)
