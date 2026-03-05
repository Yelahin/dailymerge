from django.test import TestCase
from feeds.models import ArticleModel, ArticleCategoryModel, Source
from users.models import User, UserSettings
from django.urls import reverse
from django.utils import timezone
import datetime

class ArticleListViewTestCase(TestCase):
    def setUp(self):
        self.usersettings = {}

        # Create two users with user settings
        for number in range(1, 3):
            # Create user
            user = User.objects.create_user(
                username=f"user_{number}",
                password="User1234"
            )

            user_settings, created = UserSettings.objects.get_or_create(user=user)

            # For tests
            self.usersettings[number] = user_settings

            # Create category
            category= ArticleCategoryModel.objects.create(
                name=f"Category_{number}",
                slug=f"category_{number}"
            )

            # Create UserCategory objects and set for user
            user_settings.categories.add(category)

            # Create source
            source = Source.objects.create(
                url=f"http://example.com/{number}/feed/",
            )

            # Create UserSource object and set for user
            user_settings.sources.add(source, through_defaults={'category': category})

            # Create ArticleModel object
            ArticleModel.objects.create(
                title=f"Article_{number}",
                link=f"http://example.com/article/{number}",
                published=timezone.now(),
                summary=f"Summary of article {number}",
                image_url=f"https://example.com/image.jpg",
                source=source
            )

    def test_used_template(self):
        # Check anonymous user redirects to login page from 'news'
        response = self.client.get(reverse('news'), follow=True) # follow make test follow redirects
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "users/login.html")
    
    def test_logged_in_user_redirect(self):
        # Check logged in user redirects to 'favorite' page
        self.client.login(username="user_1", password="User1234")
        response = self.client.get(reverse('news'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "users/favorite.html")

    def test_anonymous_user_redirect(self):
        # Check anonymous user redirects to login page from 'filtered_news'
        response = self.client.get(reverse('filtered_news', kwargs={'slug': 'category_1'}), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "users/login.html")

    def test_articles_display(self):
        # Check logged in user get the page with articles of chosen category
        self.client.login(username="user_1", password="User1234")
        response = self.client.get(reverse('filtered_news', kwargs={'slug': 'category_1'}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "core/index.html")

    def test_user_access_only_own_sources_results(self):
        # Test user_1 use only own category, categories display only chosen sources results
        self.client.login(username='user_1', password='User1234')

        response = self.client.get(reverse('filtered_news', kwargs={'slug': 'category_2'}))
        self.assertEqual(len(response.context['articles']), 0)
        self.assertNotContains(response, "Summary of article")

        response = self.client.get(reverse('filtered_news', kwargs={'slug': 'category_1'}))
        self.assertContains(response, "Summary of article 1")
        self.assertNotContains(response, "Summary of article 2")

        # Test user_2 use only own category, categories display only chosen sources results
        self.client.login(username='user_2', password='User1234')

        response = self.client.get(reverse('filtered_news', kwargs={'slug': 'category_1'}))
        self.assertEqual(len(response.context['articles']), 0)
        self.assertNotContains(response, "Summary of article")

        response = self.client.get(reverse('filtered_news', kwargs={'slug': 'category_2'}))
        self.assertContains(response, "Summary of article 2")
        self.assertNotContains(response, "Summary of article 1")

    def test_filtering_by_published_date(self):
        # Login user and get user settings
        self.client.login(username="user_1", password="User1234")
        usersettings = self.usersettings[1]

        # Create more articles (2 - 11), article 1 already made in setUp method
        source = usersettings.sources.get(url="http://example.com/1/feed/")
        for number in range(2, 11):
            ArticleModel.objects.create(
                title=f"Article_{number}",
                link=f"http://example.com/date/test/article/{number}",
                published=timezone.now() - datetime.timedelta(days=number),
                summary=f"Summary of article {number}",
                image_url=f"https://example.com/image.jpg",
                source=source
            )

        # Test 1: Duration of 11 days should display all articles (0-11 days old)
        usersettings.article_duration = datetime.timedelta(days=11)
        usersettings.save()

        response = self.client.get(reverse('filtered_news', kwargs={'slug': 'category_1'}))
        articles = response.context['articles']

        self.assertEqual(len(articles), 10)
        self.assertContains(response, "Summary of article 1")
        self.assertContains(response, "Summary of article 10")

        # Test 2: Duration of 5 days should display articles (0-5 days old)
        usersettings.article_duration = datetime.timedelta(days=5)
        usersettings.save()

        response = self.client.get(reverse('filtered_news', kwargs={'slug': 'category_1'}))
        articles = response.context['articles']


        self.assertEqual(len(articles), 4)
        self.assertContains(response, "Summary of article 1")
        self.assertContains(response, "Summary of article 4")

        # Test 3: Duration of 1 day should dislplay only today's article
        usersettings.article_duration = datetime.timedelta(days=1)
        usersettings.save()

        response = self.client.get(reverse('filtered_news', kwargs={'slug': 'category_1'}))
        articles = response.context['articles']

        self.assertEqual(len(articles), 1)
        self.assertContains(response, "Summary of article 1")

        # Test 4: Duration of 0 days shouldn't display any articles
        usersettings.article_duration = datetime.timedelta(days=0)
        usersettings.save()

        response = self.client.get(reverse('filtered_news', kwargs={'slug': 'category_1'}))
        articles = response.context['articles']


        self.assertEqual(len(articles), 0)
        self.assertNotContains(response, "Summary of article 1")
        