from celery import shared_task
import feedparser

@shared_task
def get_all_data(url):
    return normalize_data(url)


#normalize raw data
def normalize_data(url):
    raw_data_collection = fetch_rss_entry(url)
    result = {}
    for raw_data in raw_data_collection:
        result[raw_data.title] = {
            'title': raw_data.title,
            'link': raw_data.link,
            'published': raw_data.published,
            'summary': raw_data.summary,
            'image_url': raw_data.media_thumbnail[0]['url'],
        }
    return result

#fetch raw data from rss feeds
def fetch_rss_entry(url):
    raw_data = feedparser.parse(url)
    entries = raw_data.entries
    return entries
