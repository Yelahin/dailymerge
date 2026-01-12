import os 
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dailymerge.settings')

app = Celery('dailymerge')

published_condition = 7

app.conf.beat_schedule = {
    "upload-data": {
        "task": "feeds.tasks.upload_data",
        "schedule": 5,
        "args": (published_condition, )
    },
    "remove-data": {
        "task": "feeds.tasks.remove_data",
        "schedule": crontab(minute="*"),
        "args": (published_condition, )
    },
}

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()