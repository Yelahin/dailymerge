import os 
from celery import Celery
from celery.schedules import crontab
from feeds.feeds import API_FEEDS, RSS_FEEDS

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dailymerge.settings')

app = Celery('dailymerge')

app.conf.beat_schedule = {
    "upload-data": {
        "task": "feeds.tasks.upload_data",
        "schedule": 10,
        "args": ([RSS_FEEDS, API_FEEDS], )
    },
    "remove-data": {
        "task": "feeds.tasks.remove_data",
        "schedule": crontab(minute="*"),
    }
}

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()