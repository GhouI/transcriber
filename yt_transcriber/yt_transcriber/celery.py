import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'yt_transcriber.settings')

app = Celery('yt_transcriber')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()