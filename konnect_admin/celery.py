from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'konnect.settings')

# Create a Celery instance
app = Celery('konnect_admin')

# Load task modules from all registered Django app configs.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load tasks from all installed apps.
app.autodiscover_tasks()
