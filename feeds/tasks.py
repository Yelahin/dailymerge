from celery import shared_task
from .models import ArticleModel
import feedparser
import dateparser
from django.utils import timezone
import datetime
from bs4 import BeautifulSoup

attributes = ['title', 'link', 'published', 'summary', 'image_url']

ATTRIBUTE_PROCESSORS = {
    'title': lambda entry: entry.get('title'),
    'link': lambda entry: entry.get('link'),
    'published': lambda entry: get_published_from_entry(entry),
    'summary': lambda entry: get_summary_from_entry(entry),
    'image_url': lambda entry: get_image_url_from_entry(entry),
}

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

    

#return normalized data from feeds
def get_normalized_data(urls_list) -> list:
    result = []
    for url in urls_list:
        entries = fetch_rss_entry(url)
        result += get_entries_attributes(entries)
    return result
        
#return list of get_entry_attributes
def get_entries_attributes(entries) -> list:
    """Normalize a list of RSS feed entries into dicts."""
    entries_attributes_list = []
    for entry in entries:
        attributes_dict = get_entry_attributes(entry)
        entries_attributes_list.append(attributes_dict)
    return entries_attributes_list

#return entry attributes
def get_entry_attributes(entry) -> dict:
    """Go through entry and add attributes in dict."""
    return {attr: ATTRIBUTE_PROCESSORS[attr](entry) for attr in attributes}

#return title
def get_summary_from_entry(entry) -> str | None:
    summary = entry.get('summary')
    if summary:
        if "div" in summary:
            soup = BeautifulSoup(summary, 'html.parser')
            inner_div = soup.find_all("div")[1]
            return inner_div.get_text(strip=True)
        return summary
    return None

#return image url
def get_image_url_from_entry(entry) -> str | None:
    """This function get and return image_url from entry"""
    if "media_thumbnail" in entry:
        return entry.media_thumbnail[0].get('url')
    elif "media_content" in entry:
        return entry.media_content[0].get('url')
    return None

#return published date
def get_published_from_entry(entry) -> datetime.datetime | None:
    published = entry.get('published')
    #use if statement to prevent error of dateparser.parse(None)
    return dateparser.parse(published) if published else None

#fetch raw data from rss feeds
def fetch_rss_entry(url) -> list:
    raw_data = feedparser.parse(url)
    entries = raw_data.entries
    return entries
