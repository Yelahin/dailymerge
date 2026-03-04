from django.test import TestCase
from feeds.models import ArticleModel, Source
from feeds.utils import get_published_from_query, get_image_url_from_query, get_summary_from_query, get_query_attributes, get_queryset_attributes, filter_normalized_data
from feeds.tasks import remove_expired_articles
from django.utils import timezone
import datetime
import dateparser
from unittest.mock import AsyncMock, patch

class RemoveDataTaskTestCase(TestCase):
    def setUp(self):
        self.articles_count = 10
        source = Source.objects.create(url="http://example.com/1/feed/", source_type="RSS")
        
        for number in range(1, self.articles_count+1):
            ArticleModel.objects.create(
                title=f"Article_{number}",
                link=f"http://example.com/article/{number}",
                published=timezone.now() - datetime.timedelta(days=number),
                summary=f"Summary of article {number}",
                image_url="https://example.com/image.jpg",
                source=source
            )

    def test_remove_expired_articles_task(self):
        self.assertEqual(ArticleModel.objects.all().count(), self.articles_count)
        #remove articles 20 days old
        remove_expired_articles(20)
        self.assertEqual(ArticleModel.objects.all().count(), self.articles_count)
        #remove articles 7 days old
        remove_expired_articles(7)
        self.assertEqual(ArticleModel.objects.all().count(), 6)
        #remove all articles
        remove_expired_articles(0)
        self.assertEqual(ArticleModel.objects.all().count(), 0)


class UploadDataTaskTestCase(TestCase):
    def setUp(self):
        self.now = timezone.now()
        self.queries = [
            {
                'title': 'First title',
                'link': 'https://example.com/article/1',
                #published should be str
                'published': (self.now - datetime.timedelta(days=5)).isoformat(),
                'description': "<p><strong>Some</strong> test text!</p>",
                "media_thumbnail": [{
                    "url": "https://example.com/image.jpg",
                    "width": "240",
                    "height": "135"
                }]
            },
            {
                'title': 'Second title',
                'link': 'https://example.com/article/2',
                #published should be str
                'published': (self.now - datetime.timedelta(days=1)).isoformat(),
                'description': "<p><strong>Some</strong> test text!</p>",
                "media_thumbnail": [{
                    "url": "https://example.com/image.jpg",
                    "width": "240",
                    "height": "135"
                }]
            }
        ]
        self.query = self.queries[0]
        self.source = Source.objects.create(url="http://example.com/1/feed/", source_type="RSS")

    def test_get_published_from_query(self):
        result = get_published_from_query(self.query)
        self.assertEqual(result, dateparser.parse(self.query['published']))

    def test_get_image_url_from_query(self):
        result = get_image_url_from_query(self.query)
        self.assertEqual(result, "https://example.com/image.jpg")

    def test_get_summary_from_query(self):
        result = get_summary_from_query(self.query)
        self.assertEqual(result, "Some test text!")

    def test_get_query_attributes(self):
        result = get_query_attributes(self.query, self.source)
        expected_result = {
            'title': self.query['title'],
            'link': self.query['link'],
            'published': get_published_from_query(self.query),
            'summary': get_summary_from_query(self.query),
            'image_url': get_image_url_from_query(self.query),
            'source': self.source
        }

        self.assertEqual(result, expected_result)

    def test_get_queryset_attributes(self):
        result = get_queryset_attributes(self.queries, self.source)
        expected_result = [
            {
                'title': self.query['title'],
                'link': self.query['link'],
                'published': get_published_from_query(self.query),
                'summary': get_summary_from_query(self.query),
                'image_url': get_image_url_from_query(self.query),
                'source': self.source
            },
            {
                'title': self.queries[1]['title'],
                'link': self.queries[1]['link'],
                'published': get_published_from_query(self.queries[1]),
                'summary': get_summary_from_query(self.queries[1]),
                'image_url': get_image_url_from_query(self.queries[1]),
                'source': self.source
            }
        ]
        self.assertCountEqual(result, expected_result)

    def test_filter_normalized_data(self):
        normalized_data = get_queryset_attributes(self.queries, self.source)
        with patch('feeds.utils.check_all_images', new_callable=AsyncMock) as mock:
            mock.return_value = {"https://example.com/image.jpg"}

            #testing filter_normalized_data result

            result = filter_normalized_data(normalized_data, 10, set())
            expected_result = [ArticleModel(**article) for article in 
                               get_queryset_attributes(self.queries, self.source)]
            #check by unique field
            self.assertCountEqual([article.link for article in result],
                             [article.link for article in expected_result])
            

            #testing filter_normalized_data filter links
            
            existing_links = {self.queries[0]['link']}
            result = filter_normalized_data(normalized_data, 10, existing_links)
            expected_result = [ArticleModel(**article) for article in 
                               get_queryset_attributes(self.queries, self.source)]
            
            self.assertNotEqual([article.link for article in result],
                                [article.link for article in expected_result])

            expected_result = [ArticleModel(**article) for article in 
                               get_queryset_attributes(self.queries, self.source)
                               if article['link'] not in existing_links]
            
            self.assertCountEqual([article.link for article in result],
                             [article.link for article in expected_result])
            

            #testing filter_normalized_data filter published date


            expiring_date = 3
            result = filter_normalized_data(normalized_data, expiring_date, set())
            expected_result = [ArticleModel(**article) for article in 
                               get_queryset_attributes(self.queries, self.source)]
            
            self.assertNotEqual([article.link for article in result],
                                [article.link for article in expected_result])
            
            expected_result = [ArticleModel(**article) for article in
                               get_queryset_attributes(self.queries, self.source)
                               if article['published'] >= self.now - datetime.timedelta(days=expiring_date)]
            
            self.assertCountEqual([article.link for article in result],
                             [article.link for article in expected_result])
            