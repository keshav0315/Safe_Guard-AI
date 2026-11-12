"""
SafeGuard AI — Production Settings
Production environment ke liye — security tight, no debug, HTTPS required.
"""

from .base import *  # noqa: F401, F403
import environ

env = environ.Env()

# ---------------------------------------------------------------------------
# Security — Production mein debug NEVER on
# ---------------------------------------------------------------------------
DEBUG = False

# ALLOWED_HOSTS env se aana chahiye — comma separated
ALLOWED_HOSTS = env.list('DJANGO_ALLOWED_HOSTS')

# ---------------------------------------------------------------------------
# HTTPS / SSL Settings
# ---------------------------------------------------------------------------
SECURE_SSL_REDIRECT = True               # HTTP se HTTPS pe redirect karo
SECURE_HSTS_SECONDS = 31536000           # 1 saal HSTS
SECURE_HSTS_INCLUDE_SUBDOMAINS = True    # Subdomains bhi
SECURE_HSTS_PRELOAD = True               # HSTS preload list mein dalo
SESSION_COOKIE_SECURE = True             # Cookies sirf HTTPS pe bhejo
CSRF_COOKIE_SECURE = True                # CSRF cookie bhi HTTPS only
SECURE_BROWSER_XSS_FILTER = True         # XSS protection
SECURE_CONTENT_TYPE_NOSNIFF = True       # Content sniffing rokko
X_FRAME_OPTIONS = 'DENY'                 # Clickjacking rokko

# ---------------------------------------------------------------------------
# Static Files — WhiteNoise se serve karenge
# ---------------------------------------------------------------------------
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# ---------------------------------------------------------------------------
# Email — Production mein actual SMTP use karo
# ---------------------------------------------------------------------------
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = env('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = env.int('EMAIL_PORT', default=587)
EMAIL_USE_TLS = True
EMAIL_HOST_USER = env('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD', default='')

# ---------------------------------------------------------------------------
# CORS — Production mein sirf allowed origins
# ---------------------------------------------------------------------------
CORS_ALLOW_ALL_ORIGINS = False
# CORS_ALLOWED_ORIGINS base.py mein env se set ho raha hai

# ---------------------------------------------------------------------------
# Database — Production PostgreSQL settings
# ---------------------------------------------------------------------------
DATABASES['default']['CONN_MAX_AGE'] = 600  # noqa: F405  # 10 minutes connection pooling

# ---------------------------------------------------------------------------
# Cache — Production mein Redis
# ---------------------------------------------------------------------------
# Base settings mein Redis cache already configured hai

# ---------------------------------------------------------------------------
# Logging — Production mein ERROR level aur upar log karo
# ---------------------------------------------------------------------------
LOGGING['root']['level'] = 'WARNING'  # noqa: F405
LOGGING['handlers']['console']['level'] = 'WARNING'  # noqa: F405

# ---------------------------------------------------------------------------
# Admin URL — security ke liye custom path use karo
# ---------------------------------------------------------------------------
ADMIN_URL = env('DJANGO_ADMIN_URL', default='admin/')
