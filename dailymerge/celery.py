import os 
from celery import Celery

os.environ('DJANGO_SETTINGS_MODULE', 'dailymerge.settings')

app = Celery('dailymerge')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()