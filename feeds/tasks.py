from celery import shared_task
from .models import ArticleModel
import feedparser
import dateparser
from django.utils import timezone
import datetime

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
    normalized_data = get_entries_attributes(urls_list)
    #go through each article
    for article_data in normalized_data:
        #check if any attribute equals None
        if all(article_data.values()):
            all_params = {}
            for attribute in attributes:
                all_params[attribute] = article_data[attribute]

            
            #check if this article already exists and check if article is fresh
            existing_links = [article.link for article in ArticleModel.objects.all()]
            if all_params['link'] not in existing_links and \
            all_params['published'] >= timezone.now() - datetime.timedelta(days=published_condition):
                ArticleModel.objects.create(**all_params)

#return normalized data from feeds
def get_normalized_data(urls_list) -> list:
    result = []
    for url in urls_list:
        entries = fetch_rss_entry(url)
        result += get_entries_attributes(entries)
    return result
        
#return list of get_entry_attributes
def get_entries_attributes(entries) -> list:
    entries_attributes_list = []
    for entry in entries:
        attributes_dict = get_entry_attributes(entry)
        entries_attributes_list.append(attributes_dict)
    return entries_attributes_list

#return entry attributes
def get_entry_attributes(entry) -> dict:
    """Go through entry and add attributes in dict."""
    attributes_dict = {}
    for attribute in attributes:
        if attribute == 'image_url':
            attributes_dict[attribute] = get_image_url_from_entry(entry)
        elif attribute == 'published':
            attributes_dict[attribute] = dateparser.parse(entry[attribute])
        else:
            attributes_dict[attribute] = entry[attribute]    
    return attributes_dict

#return image url
def get_image_url_from_entry(entry) -> str:
    """This function get and return image_url from entry"""
    if "media_thumbnail" in entry:
        image_url = entry.media_thumbnail[0]['url']
    elif "media_content" in entry:
        image_url = entry.media_content[0]['url']
    return image_url

#fetch raw data from rss feeds
def fetch_rss_entry(url) -> list:
    raw_data = feedparser.parse(url)
    entries = raw_data.entries
    return entries
