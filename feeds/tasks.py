from celery import shared_task
from .models import ArticleModel
from django.utils import timezone
import datetime
from .utils import get_normalized_data

attributes = ['title', 'link', 'published', 'summary', 'image_url']

published_condition=1

#remove data from db
@shared_task
def remove_data():
    for article in ArticleModel.objects.all():
        if article.published <= timezone.now() - datetime.timedelta(days=published_condition):
            article.delete()

#upload data to db
@shared_task
def upload_data(urls_list):
    normalized_data = get_normalized_data(urls_list)

    #to check that article are unique
    existing_links = set(ArticleModel.objects.values_list('link', flat=True))
    #to check that article is not old
    expiration_date = timezone.now() - datetime.timedelta(days=published_condition)

    new_articles = []
    for article in normalized_data:
        #check if any attribute equals None
        if not all(article.values()):
            continue

        link = article['link']

        if link not in existing_links \
        and article['published'] >= expiration_date:
            #append ArticleModel instance to pass bulk_create
            new_articles.append(ArticleModel(**article))
            existing_links.add(link)

    if new_articles:
        ArticleModel.objects.bulk_create(new_articles)
