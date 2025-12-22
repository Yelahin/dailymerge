from celery import shared_task
from .models import ArticleModel
import feedparser
import dateparser

attributes = ['title', 'link', 'published', 'summary', 'image_url']

#upload data to db
@shared_task
def upload_data(url):
    normalized_data = normalize_data(url)
    #go through each article
    for article_data in normalized_data:
        #check if any attribute equals None
        if all(article_data.values()):
            all_params = {}
            for attribute in attributes:
                all_params[attribute] = article_data[attribute]

            #check if this article already exists
            existing_links = [article.link for article in ArticleModel.objects.all()]
            if all_params['link'] not in existing_links:
                ArticleModel.objects.create(**all_params)

#normalize raw data
def normalize_data(url) -> list:
    raw_data_collection = fetch_rss_entry(url)
    result = []
    #go through each article
    for raw_data in raw_data_collection:
        article_data = {}
        #go through each attribute
        for attribute in attributes:
            #feedparser don't use "image_url" tag - instead it use "media_thumbnail"
            if attribute == 'image_url':
                article_data[attribute] = raw_data.media_thumbnail[0]['url']
            #transform published time format - to pass DateTimeField in .models
            elif attribute == 'published':
                article_data[attribute] = dateparser.parse(raw_data[attribute])
            else:
                article_data[attribute] = raw_data[attribute]
        #add article to result
        result.append(article_data)
    return result

#fetch raw data from rss feeds
def fetch_rss_entry(url):
    raw_data = feedparser.parse(url)
    entries = raw_data.entries
    return entries
