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
                #World News
                "https://feeds.bbci.co.uk/news/world/rss.xml", #world news +
                "https://www.theguardian.com/world/rss", #world news +
                "https://www.dailymail.co.uk/home/index.rss", #world news +

                #Politics News
                "https://rss.app/feeds/tFPubwkQz33TawYL.xml", #EU politics +
                "https://rss.app/feeds/tM4rTuFUu0bLwKgS.xml", #US politics +
                "https://rss.app/feeds/tGiu9CqL75md2Hcs.xml", #China politics +
                "https://rss.app/feeds/tLIJILshtpaHgTYQ.xml", #Ukraine war politics +
                "https://rss.app/feeds/tMUmTyRbNx0UVHKS.xml", #Russia politics +
                "https://rss.politico.com/congress.xml", #Congress politics +
                "https://rss.politico.com/defense.xml", #Defense politics +

                #Sport News
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