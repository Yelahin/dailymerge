from celery import shared_task
from .models import ArticleModel
from django.utils import timezone
import datetime
from .utils import get_normalized_data, check_all_images
import asyncio

published_condition=1

#remove data from db
@shared_task
def remove_data():
    expiring_data = timezone.now() - datetime.timedelta(days=published_condition)
    for article in ArticleModel.objects.all():
        if article.published <= expiring_data:
            article.delete()

#upload data to db
@shared_task
def upload_data(feeds_urls: dict):
    normalized_data = get_normalized_data(feeds_urls)

    #to check that article are unique
    existing_links = set(ArticleModel.objects.values_list('link', flat=True))
    #to check that article is not old    
    expiring_data = timezone.now() - datetime.timedelta(days=published_condition)

    filtered_articles = []
    for article in normalized_data:
        if not all(article.values()):
            continue

        link = article['link']

        if link not in existing_links \
        and article['published'] >= expiring_data:
            #append ArticleModel instance to pass bulk_create
            filtered_articles.append(article)
            existing_links.add(link)

    images_urls = (article['image_url'] for article in filtered_articles)

    valid_images_urls = asyncio.run(check_all_images(images_urls))

    new_articles = [ArticleModel(**article) for article in filtered_articles
                    if article['image_url'] in valid_images_urls]


    if new_articles:
        ArticleModel.objects.bulk_create(new_articles, ignore_conflicts=True, batch_size=1000)
