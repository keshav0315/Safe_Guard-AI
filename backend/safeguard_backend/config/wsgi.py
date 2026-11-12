"""
SafeGuard AI — WSGI Configuration
Production deployment ke liye (Gunicorn, uWSGI, etc.)
"""

import os
import sys
from pathlib import Path

# safeguard_backend ko Python path mein add karo taaki 'config', 'apps' imports kaam karein
# Backend root → manage.py wali directory
_backend_root = Path(__file__).resolve().parent.parent.parent  # backend/
_safeguard_pkg = _backend_root / 'safeguard_backend'

if str(_backend_root) not in sys.path:
    sys.path.insert(0, str(_backend_root))
if str(_safeguard_pkg) not in sys.path:
    sys.path.insert(0, str(_safeguard_pkg))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')

from django.core.wsgi import get_wsgi_application  # noqa: E402

application = get_wsgi_application()
