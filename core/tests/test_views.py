from django.test import TestCase
from feeds.models import ArticleModel, ArticleCategoryModel
from django.utils import timezone
from django.urls import reverse

class ArticleListViewTestCase(TestCase):
    def setUp(self):
        category_1 = ArticleCategoryModel.objects.create(name="World News")
        category_2 = ArticleCategoryModel.objects.create(name="Sport News")
        #Article of World News category
        ArticleModel.objects.create(
            title="World News",
            link="link_1",
            published=timezone.now(),
            summary="Summary of world news",
            image_url="image_url",
            category_id=category_1.id)
        #Article of Sport News category
        ArticleModel.objects.create(
            title="Sport News",
            link="link_2",
            published=timezone.now(),
            summary="Summary of sport news",
            image_url="image_url",
            category_id=category_2.id
        )
        
    def test_news_page_use_correct_template(self):
        response = self.client.get(reverse('filtered_news', kwargs={'slug': 'world-news'}))
        self.assertTemplateUsed(response, 'core/index.html')
        self.assertTemplateUsed(response, 'basic.html')

    def test_news_page_categories_and_page_content(self):
        response = self.client.get(reverse('filtered_news', kwargs={'slug': 'world-news'}))
        self.assertContains(response, 'Summary of world news')
        self.assertNotContains(response, 'Summary of sport news')

        response = self.client.get(reverse('filtered_news', kwargs={'slug': 'sport-news'}))
        self.assertContains(response, 'Summary of sport news')
        self.assertNotContains(response, 'Summary of world news')

        for category in ArticleCategoryModel.objects.all():
            self.assertContains(response, category.name)
