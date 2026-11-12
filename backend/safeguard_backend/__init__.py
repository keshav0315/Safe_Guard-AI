# SafeGuard AI Backend package
# Celery app ko load karna taaki @shared_task use ho sake
from infrastructure.celery.app import app as celery_app

__all__ = ('celery_app',)
