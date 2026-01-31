import os 
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dailymerge.settings')

app = Celery('dailymerge')

published_condition = 365

app.conf.beat_schedule = {
    "upload-articles": {
        "task": "feeds.tasks.upload_articles",
        "schedule": 5,
        "args": (published_condition, )
    },
    "remove-expired-articles": {
        "task": "feeds.tasks.remove_expired_articles",
        "schedule": 5,
        "args": (published_condition, )
    },
}

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()