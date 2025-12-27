import os 
from celery import Celery
from celery.schedules import crontab
from feeds.feeds import FEEDS_URLS

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dailymerge.settings')

app = Celery('dailymerge')

app.conf.beat_schedule = {
    "upload-data": {
        "task": "feeds.tasks.upload_data",
        "schedule": 5,
        "args": (FEEDS_URLS, )
    },
    "remove-data": {
        "task": "feeds.tasks.remove_data",
        "shcedule": crontab(minute="*"),
    }
}

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()