import feedparser
import dateparser
import datetime
from bs4 import BeautifulSoup
import re

ATTRIBUTE_PROCESSORS = {
    'title': lambda entry: entry.get('title'),
    'link': lambda entry: entry.get('link'),
    'published': lambda entry: get_published_from_entry(entry),
    'summary': lambda entry: get_summary_from_entry(entry),
    'image_url': lambda entry: get_image_url_from_entry(entry),
}


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
    return {attr: processor(entry) for attr, processor in ATTRIBUTE_PROCESSORS.items()}

#return title
def get_summary_from_entry(entry) -> str | None:
    summary = entry.get('summary')
    if summary:
        soup = BeautifulSoup(summary, 'html.parser')
        return soup.get_text()
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
