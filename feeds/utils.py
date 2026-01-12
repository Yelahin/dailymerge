import feedparser
import dateparser
import datetime
from bs4 import BeautifulSoup
from .models import ArticleModel, APIFeed, RSSFeed
import asyncio
import aiohttp
import ssl
import certifi
import requests
from django.utils import timezone

ATTRIBUTE_PROCESSORS = {
    'title': lambda query: query.get('title'),
    'link': lambda query: query.get('link') or query.get('url'),
    'published': lambda query: get_published_from_query(query),
    'summary': lambda query: get_summary_from_query(query),
    'image_url': lambda query: get_image_url_from_query(query),
}


#Normalized data functions

def filter_normalized_data(normalized_data: list[dict[str: any]],
                           published_condition: int,
                           existing_links: set[str]) -> list[ArticleModel]:
    
    """
    This function returns list of filtered ArticleModel objects

    This function also checks:
    - All attributes in each article != None
    - Each article have unique link
    - Each article have valid published date
    - Each article have valid image url
    """

    expiring_date = timezone.now() - datetime.timedelta(days=published_condition)

    filtered_articles = []
    for article in normalized_data:
        if any(value is None for value in article.values()):
            continue

        link = article['link']

        if link not in existing_links \
        and article['published'] >= expiring_date:
            filtered_articles.append(article)

    images_urls = (article['image_url'] for article in filtered_articles)
    valid_images_urls = asyncio.run(check_all_images(images_urls))

    valid_articles = [ArticleModel(**article) for article in filtered_articles
                if article['image_url'] in valid_images_urls]
    
    return valid_articles

def get_normalized_data(feeds: list[RSSFeed | APIFeed]) -> list[dict[str: any]]:
    """This function returns normalized data from feed urls"""
    result = []
    for feed in feeds:
        if isinstance(feed, RSSFeed):
            queryset = fetch_rss_entry(feed)
        else:
            queryset = fetch_api_feeds(feed)
        result += get_queryset_attributes(queryset, feed.category.id)
    return result


#Get attributes functions

def get_queryset_attributes(queryset: list, category: int) -> list[dict[str: any]]:
    """This function returns list of dicts with query attributes"""
    queryset_attributes_list = []
    for query in queryset:
        attributes_dict = get_query_attributes(query, category)
        queryset_attributes_list.append(attributes_dict)
    return queryset_attributes_list

def get_query_attributes(query: dict, category: int) -> dict[str: any]:
    """This function returns dict of querys attributes"""
    article_attributes = {attr: processor(query) for attr, processor in ATTRIBUTE_PROCESSORS.items()}
    article_attributes['category_id'] = category
    return article_attributes


#Get attributes from query functions

def get_summary_from_query(query: dict) -> str | None:
    """This function returns summary from query without html"""
    summary = query.get('summary') or query.get('description')
    if summary:
        soup = BeautifulSoup(summary, 'html.parser')
        return soup.get_text()
    return None

def get_image_url_from_query(query: dict) -> str | None:
    """Thins function returns image url or None from query"""
    if 'media_thumbnail' in query:
        return get_image_url_from_tag(query, 'media_thumbnail')
        
    elif 'media_content' in query:
        return get_image_url_from_tag(query, 'media_content')
    
    elif 'enclosure' in query:
        return get_image_url_from_tag(query, 'enclosure')
    
    if 'urlToImage' in query:
        return query['urlToImage']
    
    return None

def get_published_from_query(query: dict) -> datetime.datetime | None:
    """This function returns published date from query in datetime.datetime format"""
    published = query.get('published') or query.get('publishedAt')
    #use if statement to prevent error of dateparser.parse(None)
    return dateparser.parse(published) if published else None


#Fetching functions

def fetch_rss_entry(rss: RSSFeed) -> list:
    """This function fetchs data from rss feeds"""
    raw_data = feedparser.parse(rss.url)
    entries = raw_data.entries
    return entries

def fetch_api_feeds(api: APIFeed) -> list:
    """This function fetchs data from API feeds"""
    response = requests.get(api.url, params=api.params)
    json = response.json()
    articles = json['articles']
    return articles


#Image attributes functions

async def check_all_images(image_urls) -> set[str]:
    """This function checks all image urls"""
    sslcontext = ssl.create_default_context(cafile=certifi.where())
    connector = aiohttp.TCPConnector(ssl=sslcontext)
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = (check_image_url(session, image_url) for image_url in image_urls)
        result = await asyncio.gather(*tasks)

    return {image_url for image_url in result if image_url}

async def check_image_url(session, image_url: str) -> str | None:
    """This function checks if image url return 200 status code before timeout"""
    try:
        async with session.get(
            image_url,
            timeout=aiohttp.ClientTimeout(total=5)
        ) as response:
            if response.status == 200:
                return image_url
    except (aiohttp.ClientError, asyncio.TimeoutError):
        return None

def get_image_url_from_tag(query: dict, tag: str) -> str:
    """This function returns image url from query using tag"""
    tag_data = query.get(tag, [])
    if tag_data and tag_data[0].get('url'):
        return tag_data[0]['url']
    