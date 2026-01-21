from celery import shared_task
from .models import ArticleModel, RSSFeed, APIFeed
from django.utils import timezone
import datetime
from .utils import get_normalized_data, filter_normalized_data

#remove data from db
@shared_task
def remove_data(published_condition: int):
    expiring_data = timezone.now() - datetime.timedelta(days=published_condition)
    ArticleModel.objects.filter(published__lt=expiring_data).delete()

#upload data to db
@shared_task
def upload_data(published_condition: int):
    feed_sources = [
        [feed for feed in RSSFeed.objects.filter(active=True)],
        [feed for feed in APIFeed.objects.filter(active=True)]
    ]
    for feeds in feed_sources:
        normalized_data = get_normalized_data(feeds)

        existing_links = set(ArticleModel.objects.values_list('link', flat=True))

        new_articles = filter_normalized_data(normalized_data, published_condition, existing_links)

        existing_links.update(article.link for article in new_articles)

        if new_articles:
            ArticleModel.objects.bulk_create(new_articles, ignore_conflicts=True, batch_size=1000)
