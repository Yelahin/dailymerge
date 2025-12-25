import os 
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dailymerge.settings')

app = Celery('dailymerge')

app.conf.beat_schedule = {
    "upload-data": {
        "task": "feeds.tasks.upload_data",
        "schedule": 5,
        "args": (
            [
                "https://feeds.bbci.co.uk/news/world/rss.xml", #world news
                "https://feeds.bbci.co.uk/news/rss.xml", #world news
                "https://rss.app/feeds/twV4dtLhEH4l9cRG.xml", #ufc news
            ], 
        )
    },
    "remove-data": {
        "task": "feeds.tasks.remove_data",
        "shcedule": crontab(minute="*"),
    }
}

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()