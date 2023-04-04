import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

celery = Celery("social_events")
celery.config_from_object("django.conf:settings", namespace="CELERY")
celery.autodiscover_tasks()
