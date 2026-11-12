# Celery app configuration - background tasks ke liye

import os
from celery import Celery

# Django settings set karo Celery ke liye
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')

app = Celery('safeguard_backend')

# Config Django settings se lo
app.config_from_object('django.conf:settings', namespace='CELERY')

# Automatically tasks discover karo sare apps se
app.autodiscover_tasks()

@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
