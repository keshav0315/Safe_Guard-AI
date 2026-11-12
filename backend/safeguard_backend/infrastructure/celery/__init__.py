# Celery app ko Django ke __init__.py se load karna
from .app import app as celery_app
__all__ = ('celery_app',)
