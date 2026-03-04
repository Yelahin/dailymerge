import json
from django.test import TestCase
from users.models import User, UserCategory, UserSource
from feeds.models import ArticleModel, ArticleCategoryModel, Source
from django.urls import reverse
from django.utils import timezone
import datetime


class SignUpViewTestCase(TestCase):
    def setUp(self):
        self.form_data = {
            "username": "new_user",
            "email": "new_user@example.com",
            "password1": "ExamplePassword1234!",
            "password2": "ExamplePassword1234!"
        }

    def test_signup_template(self):
        response = self.client.get(reverse('sign_up'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "users/signup.html")

    def test_signup_valid_form(self):
        # Test 1: Valid form data
        response = self.client.post(reverse('sign_up'), data=self.form_data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username="new_user").exists())

        # Test 2: Max length username
        form_data = self.form_data.copy()
        form_data["username"] = "n" * 50
        response = self.client.post(reverse('sign_up'), data=form_data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username="n" * 50).exists())

        # Test 3: Min length username
        form_data = self.form_data.copy()
        form_data["username"] = "nn"
        response = self.client.post(reverse('sign_up'), data=form_data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username="nn").exists())

    def test_signup_invalid_empty_form(self):
        form_data = {}
        response = self.client.post(reverse('sign_up'), data=form_data)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.all().exists())

    def test_signup_form_invalid_username(self):
        # Test 1: Empty username
        form_data = self.form_data.copy()
        form_data["username"] = ""
        response = self.client.post(reverse('sign_up'), data=form_data)
        self.assertFalse(User.objects.all().exists())

        # Test 2: Too short username
        form_data = self.form_data.copy()
        form_data["username"] = "n"
        response = self.client.post(reverse('sign_up'), data=form_data)
        self.assertFalse(User.objects.all().exists())

        # Test 3: Too long username
        form_data["username"] = "n" * 51
        response = self.client.post(reverse('sign_up'), data=form_data)
        self.assertFalse(User.objects.all().exists())

    def test_signup_form_invalid_email(self):
        form_data = self.form_data.copy()
        form_data["email"] = "invalid_email"
        response = self.client.post(reverse('sign_up'), data=form_data)
        self.assertFalse(User.objects.all().exists())

    def test_signup_form_invalid_password(self):
        # Test 1: Empty password
        form_data = self.form_data.copy()
        form_data["password1"] = ""
        form_data["password2"] = ""
        response = self.client.post(reverse('sign_up'), data=form_data)
        self.assertFalse(User.objects.all().exists())

        # Test 2: Passwords do not match
        form_data = self.form_data.copy()
        form_data["password1"] = "ExamplePassword1234!"
        form_data["password2"] = "DifferentPassword1234!"
        response = self.client.post(reverse('sign_up'), data=form_data)
        self.assertFalse(User.objects.all().exists())

        # Test 3: Password too short
        form_data = self.form_data.copy()
        form_data["password1"] = "short"
        form_data["password2"] = "short"
        response = self.client.post(reverse('sign_up'), data=form_data)
        self.assertFalse(User.objects.all().exists())

        # Test 4: Password too common
        form_data = self.form_data.copy()
        form_data["password1"] = "password"
        form_data["password2"] = "password"
        response = self.client.post(reverse('sign_up'), data=form_data)
        self.assertFalse(User.objects.all().exists())


class LoginViewTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="user_1", password="User1234")

    def test_login_template(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "users/login.html")

    def test_login_valid_credentials(self):
        form_data = {"username": "user_1", "password": "User1234"}
        response = self.client.post(reverse('login'), data=form_data)
        self.assertEqual(response.status_code, 302)

    def test_login_invalid_credentials(self):
        form_data = {"username": "user_1", "password": "WrongPassword"}
        response = self.client.post(reverse('login'), data=form_data)
        self.assertEqual(response.status_code, 200)


class LoginRequiredMixinTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="user_1", password="User1234")    
    
    def test_redirect_anonymous_users(self):
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 302)

    def test_redirect_anonymous_users_template(self):
        response = self.client.get(reverse('profile'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "users/login.html")

    def test_logged_in_user(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "users/profile.html")


class ProfileViewTestCase(TestCase):
    username = "user_1"
    password = "User1234"

    def setUp(self):
        # Create user/usersettings
        self.user = User.objects.create_user(username="user_1", password=self.password)
        self.usersettings = self.user.usersettings

        # Login user
        self.client.force_login(self.user)

        # Create category
        self.category, created = ArticleCategoryModel.objects.get_or_create(
            name="Category_1",
            slug="category_1"
        )

        # Set category
        self.user.usersettings.categories.add(self.category)

        # Create source
        self.source, created = Source.objects.get_or_create(
            url="http://example.com/feed/",
            source_type="RSS"
        )

        # Set source 
        self.user.usersettings.sources.add(self.source, through_defaults={'category': self.category})

    def test_profile_template(self):
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "users/profile.html")

    def test_profile_display_username(self):
        response = self.client.get(reverse('profile'))
        self.assertContains(response, self.user.username)

    def test_profile_display_articles_duration(self):
        usersettings = self.usersettings

        duration_value_1 = 35
        duration_value_2 = 95

        # Test 1: Display current value(duration_value_1)
        usersettings.article_duration = datetime.timedelta(days=duration_value_1)
        usersettings.save()
        response = self.client.get(reverse('profile'))
        self.assertContains(response, duration_value_1)
        self.assertNotContains(response, duration_value_2)

        # Test 2: Display value after update(duration_value_2)
        usersettings.article_duration = datetime.timedelta(days=duration_value_2)
        usersettings.save()
        response = self.client.get(reverse('profile'))
        self.assertContains(response, duration_value_2)
        self.assertNotContains(response, duration_value_1)

    def test_profile_display_categories(self):
        # Test 1: Check categories display
        response = self.client.get(reverse("profile"))
        self.assertContains(response, "Category_1")

        # Test 2: Check categories display after updating
        category = ArticleCategoryModel.objects.get(name="Category_1")
        category.name = "Updated_Category"
        category.save()
        response = self.client.get(reverse("profile"))
        self.assertNotContains(response, "Category_1")
        self.assertContains(response, "Updated_Category")

        # Test 3: Check categories display after deleting
        category.delete()
        response = self.client.get(reverse("profile"))
        self.assertNotContains(response, "Category_1")
        self.assertNotContains(response, "Updated_Category")
        
    def test_profile_display_sources(self):
        # Test 1: Check sources display
        response = self.client.get(reverse('profile'))
        self.assertContains(response, "http://example.com/feed/")

        # Test 2: Check sources display after updating
        source = Source.objects.get(url="http://example.com/feed/")
        source.url = "http://example.com/another-feed/"
        source.save()
        response = self.client.get(reverse('profile'))
        self.assertNotContains(response, "http://example.com/feed/")
        self.assertContains(response, "http://example.com/another-feed/")

        # Test 3: Check sources after deleting
        source.delete()
        response = self.client.get(reverse('profile'))
        self.assertNotContains(response, "http://example.com/another-feed/")
        self.assertNotContains(response, "http://example.com/feed/")

    def test_profile_check_delete_source(self):
        self.assertEqual(self.user.usersettings.sources.count(), 1)
        response = self.client.post(reverse("profile"), data={f"delete_{Source.__name__.lower()}": self.user.usersettings.sources.first().pk})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.user.usersettings.sources.count(), 0)

    def test_profile_check_delete_same_source_for_different_users(self):
        # Create another user with same source
        user_2 = User.objects.create_user(username="user_2", password="User1234")
        user_2.usersettings.sources.add(self.source, through_defaults={'category': self.category})

        self.assertEqual(user_2.usersettings.sources.count(), 1)
        self.assertEqual(self.user.usersettings.sources.count(), 1)
        self.assertEqual(Source.objects.count(), 1)
        self.assertEqual(UserSource.objects.count(), 2)

        # Delete source for user_1
        resposne = self.client.post(reverse("profile"), data={f"delete_{Source.__name__.lower()}": self.user.usersettings.sources.first().pk})
        self.assertEqual(resposne.status_code, 302)
        self.assertEqual(self.user.usersettings.sources.count(), 0)
        self.assertEqual(user_2.usersettings.sources.count(), 1)
        self.assertEqual(Source.objects.count(), 1)
        self.assertEqual(UserSource.objects.count(), 1)

    def test_profile_check_delete_category(self):
        self.assertEqual(self.user.usersettings.categories.count(), 1)
        response = self.client.post(reverse("profile"), data={f"delete_{ArticleCategoryModel.__name__.lower()}": self.user.usersettings.categories.first().pk})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.user.usersettings.categories.count(), 0)

    def test_profile_check_delete_same_category_for_different_users(self):
        # Create another user with same category
        user_2 = User.objects.create_user(username="user_2", password="User1234")
        user_2.usersettings.categories.add(self.category)

        self.assertEqual(user_2.usersettings.categories.count(), 1)
        self.assertEqual(self.user.usersettings.categories.count(), 1)
        self.assertEqual(ArticleCategoryModel.objects.count(), 1)
        self.assertEqual(UserCategory.objects.count(), 2)

        # Delete category for user_1
        resposne = self.client.post(reverse("profile"), data={f"delete_{ArticleCategoryModel.__name__.lower()}": self.user.usersettings.categories.first().pk})
        self.assertEqual(resposne.status_code, 302)
        self.assertEqual(self.user.usersettings.categories.count(), 0)
        self.assertEqual(user_2.usersettings.categories.count(), 1)
        self.assertEqual(ArticleCategoryModel.objects.count(), 1)
        self.assertEqual(UserCategory.objects.count(), 1)

    def test_profile_check_delete_category_with_user_source(self):
        # Check that category is deleted with user source
        self.assertEqual(self.user.usersettings.categories.count(), 1)
        self.assertEqual(self.user.usersettings.sources.count(), 1)
        response = self.client.post(reverse("profile"), data={f"delete_{ArticleCategoryModel.__name__.lower()}": self.user.usersettings.categories.first().pk})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.user.usersettings.categories.count(), 0)
        self.assertEqual(self.user.usersettings.sources.count(), 0)


class ToggleFavoriteViewTestCase(TestCase):
    def setUp(self):
        # Create user and login
        self.user = self.user = User.objects.create_user(username="user_1", password="User1234")
        self.client.force_login(self.user)

        # Create source
        source = Source.objects.create(
            url="http://example.com/feed/",
            source_type="RSS"
        )

        # Create article
        self.article = ArticleModel.objects.create(
            title="Article_1",
            link="http://example.com/article/1",
            published=timezone.now(),
            summary="Summary of article 1",
            image_url="https://example.com/image.jpg",
            source=source
        )

    def test_toggle_favorite_add_article(self):
        self.assertTrue(self.user.usersettings.favorite_articles.count() == 0)
        url = reverse("toggle_favorite", kwargs={"pk": self.article.pk})
        self.client.post(url)
        self.assertTrue(self.user.usersettings.favorite_articles.count() == 1)
        self.assertTrue(self.user.usersettings.favorite_articles.filter(pk=self.article.pk).exists())

    def test_toggle_favorite_remove_article(self):
        # Add article to favorites
        self.user.usersettings.favorite_articles.add(self.article)
        self.assertTrue(self.user.usersettings.favorite_articles.count() == 1)

        # Remove article from favorites
        url = reverse("toggle_favorite", kwargs={"pk": self.article.pk})
        self.client.post(url)
        self.assertTrue(self.user.usersettings.favorite_articles.count() == 0)
        self.assertFalse(self.user.usersettings.favorite_articles.filter(pk=self.article.pk).exists())
        

class FavoriteArticlesViewTestCase(TestCase):
    def setUp(self):
        # Create user
        self.user = User.objects.create_user(username="user_1", password="User1234")

        # Login user
        self.client.force_login(self.user)

        # Create source
        source = Source.objects.create(
            url="http://example.com/feed/",
            source_type="RSS"
        )

        self.articles_amount = 5

        for number in range(1, self.articles_amount+1):
            # Create article
            article = ArticleModel.objects.create(
                title=f"Article_{number}",
                link=f"http://example.com/article/{number}",
                published=timezone.now() - datetime.timedelta(days=number),
                summary=f"Summary of article {number}",
                image_url=f"https://example.com/image.jpg",
                source=source
            )
            self.user.usersettings.favorite_articles.add(article)

    def test_favorite_page_template(self):
        response = self.client.get(reverse('favorite'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "users/favorite.html")

    def test_favorite_page_context(self):
        response = self.client.get(reverse("favorite"))
        self.assertEqual(len(response.context['articles']), self.articles_amount)
        self.assertContains(response, "Summary of article 1")
        self.assertContains(response, f"Summary of article {self.articles_amount}")

    def test_favorite_page_remove_article(self):
        # Check article displays on favorite page 
        response = self.client.get(reverse("favorite"))
        self.assertContains(response, "Summary of article 1")
        self.assertEqual(len(response.context['articles']), self.articles_amount)
        
        # Remove article from faborites
        article_to_remove = self.user.usersettings.favorite_articles.get(title="Article_1")
        self.user.usersettings.favorite_articles.remove(article_to_remove)
        response = self.client.get(reverse("favorite"))
        self.assertNotContains(response, "Summary of article 1")
        self.assertEqual(len(response.context['articles']), self.articles_amount-1)


class CategoryCreateViewTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="user_1", password="User1234")
        self.client.force_login(self.user)

    def test_category_create_template(self):
        response = self.client.get(reverse("category_create"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "users/category_create_form.html")

    def test_category_create_empty_form(self):
        form_data = {"name": "", "slug": ""}
        response = self.client.post(reverse("category_create"), data=form_data)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(ArticleCategoryModel.objects.all().exists())
        self.assertFalse(self.user.usersettings.categories.all().exists())

    def test_category_create_valid_form(self):
        form_data = {"name": "Category_1", "slug": "category_1"}
        response = self.client.post(reverse("category_create"), data=form_data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(ArticleCategoryModel.objects.filter(name="Category_1").exists())
        self.assertTrue(self.user.usersettings.categories.filter(name="Category_1").exists())

    def test_category_create_duplicate_name(self):
        # Create category with name "Category_1"
        category = ArticleCategoryModel.objects.create(name="Category_1", slug="category_1")
        self.user.usersettings.categories.add(category)

        # Try to create category with the same name
        form_data = {"name": "Category_1", "slug": "category_2"}
        response = self.client.post(reverse("category_create"), data=form_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(ArticleCategoryModel.objects.filter(name="Category_1").count(), 1)
        self.assertEqual(self.user.usersettings.categories.filter(name="Category_1").count(), 1)

    def test_category_create_duplicate_slug(self):
        # Create category with slug "category_1"
        category = ArticleCategoryModel.objects.create(name="Category_1", slug="category_1")
        self.user.usersettings.categories.add(category)

        # Try to create category with the same slug
        form_data = {"name": "Category_2", "slug": "category_1"}
        response = self.client.post(reverse("category_create"), data=form_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(ArticleCategoryModel.objects.filter(slug="category_1").count(), 1)
        self.assertEqual(self.user.usersettings.categories.filter(slug="category_1").count(), 1)

    def test_category_create_merge_same_categories_for_different_users(self):
        # Create category with name "Category_1" for user_1
        ArticleCategoryModel.objects.create(name="Category_1", slug="category_1")
        self.user.usersettings.categories.add(ArticleCategoryModel.objects.get(name="Category_1"))
        self.assertEqual(ArticleCategoryModel.objects.filter(name="Category_1").count(), 1)
        self.assertTrue(self.user.usersettings.categories.filter(name="Category_1").exists())

        # Create another user
        user_2 = User.objects.create_user(username="user_2", password="User1234")
        self.client.force_login(user_2)

        # Create category with the same name for user_2
        form_data = {"name": "Category_1", "slug": "category_1"}
        response = self.client.post(reverse("category_create"), data=form_data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(ArticleCategoryModel.objects.filter(name="Category_1").count(), 1)
        self.assertTrue(user_2.usersettings.categories.filter(name="Category_1").exists())


class SourceCreateViewTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="user_1", password="User1234")
        self.client.force_login(self.user)

        # Create category for sources
        self.category = ArticleCategoryModel.objects.create(name="Category_1", slug="category_1")
        self.user.usersettings.categories.add(self.category)

    def test_source_create_template(self):
        response = self.client.get(reverse("source_create"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "users/source_create_form.html")

    def test_source_create_empty_form(self):
        form_data = {"url": "", "source_type": ""}
        response = self.client.post(reverse("source_create"), data=form_data)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Source.objects.all().exists())
        self.assertFalse(UserSource.objects.all().exists())

    def test_source_create_valid_form(self):
        # Test 1: Create source with RSS type
        form_data = {"url": "http://example.com/feed/", "source_type": "RSS", "category": self.category.pk}
        response = self.client.post(reverse("source_create"), data=form_data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Source.objects.filter(url="http://example.com/feed/").exists())
        self.assertTrue(UserSource.objects.filter(usersettings=self.user.usersettings, source__url="http://example.com/feed/").exists())

        # Test 2: Create source with API type and params
        form_data = {"url": "http://example.com/another-feed/", 
                     "source_type": "API", 
                     "params": json.dumps({"param1": "value1", "param2": "value2"}),
                     "category": self.category.pk}
        
        response = self.client.post(reverse("source_create"), data=form_data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Source.objects.filter(url="http://example.com/another-feed/").exists())
        self.assertTrue(UserSource.objects.filter(usersettings=self.user.usersettings, source__url="http://example.com/another-feed/").exists())

    def test_source_create_duplicate_url(self):
        # Create source with url "http://example.com/feed/"
        source = Source.objects.create(url="http://example.com/feed/", source_type="RSS")
        UserSource.objects.create(usersettings=self.user.usersettings, source=source, category=self.category)
        self.assertEqual(Source.objects.filter(url="http://example.com/feed/").count(), 1)
        self.assertEqual(self.user.usersettings.sources.filter(url="http://example.com/feed/").count(), 1)

        # Try to create source with the same url
        form_data = {"url": "http://example.com/feed/", "source_type": "RSS", "category": self.category.pk}
        response = self.client.post(reverse("source_create"), data=form_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Source.objects.filter(url="http://example.com/feed/").count(), 1)
        self.assertEqual(self.user.usersettings.sources.filter(url="http://example.com/feed/").count(), 1)


class CategoryUpdateViewTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="user_1", password="User1234")
        self.client.force_login(self.user)

        # Create category
        self.category = ArticleCategoryModel.objects.create(name="Category_1", slug="category_1")
        self.user.usersettings.categories.add(self.category)

    def test_category_update_template(self):
        response = self.client.get(reverse("category_update", kwargs={"pk": self.category.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "users/category_update_form.html")

    def test_category_update_empty_form(self):
        form_data = {"name": "", "slug": ""}
        response = self.client.post(reverse("category_update", kwargs={"pk": self.category.pk}), data=form_data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(ArticleCategoryModel.objects.filter(pk=self.category.pk).exists())
        self.assertTrue(self.user.usersettings.categories.filter(pk=self.category.pk).exists())
        self.assertEqual(ArticleCategoryModel.objects.count(), 1)

    def test_category_update_valid_form(self):
        form_data = {"name": "Updated_Category", "slug": "updated_category"}
        response = self.client.post(reverse("category_update", kwargs={"pk": self.category.pk}), data=form_data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(ArticleCategoryModel.objects.filter(name="Updated_Category").exists())
        self.assertTrue(self.user.usersettings.categories.filter(name="Updated_Category").exists())
        self.assertFalse(ArticleCategoryModel.objects.filter(name="Category_1").exists()) 
        self.assertFalse(self.user.usersettings.categories.filter(name="Category_1").exists())
        self.assertEqual(ArticleCategoryModel.objects.count(), 1)

    def test_category_update_duplicate_name(self):
        # Create another category with name "Category_2"
        category_2 = ArticleCategoryModel.objects.create(name="Category_2", slug="category_2")
        self.user.usersettings.categories.add(category_2)

        # Try to update category_1 with the same name as category_2
        form_data = {"name": "Category_2", "slug": "updated_category"}
        response = self.client.post(reverse("category_update", kwargs={"pk": self.category.pk}), data=form_data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(ArticleCategoryModel.objects.filter(name="Category_1").exists())
        self.assertTrue(self.user.usersettings.categories.filter(name="Category_1").exists())
        self.assertTrue(ArticleCategoryModel.objects.filter(name="Category_2").exists())
        self.assertTrue(self.user.usersettings.categories.filter(name="Category_2").exists())
        self.assertEqual(ArticleCategoryModel.objects.count(), 2)

    def test_category_update_merge_same_categories_for_different_users(self):
        # Create another user
        user_2 = User.objects.create_user(username="user_2", password="User1234")
        self.client.force_login(user_2)

        # Create category for user_2 with different name but the same slug as category_1
        category = ArticleCategoryModel.objects.create(name="Another_Category", slug="category_1")
        user_2.usersettings.categories.add(category)
        self.assertEqual(ArticleCategoryModel.objects.filter(slug="category_1").count(), 2)
        self.assertTrue(user_2.usersettings.categories.filter(name="Another_Category").exists())

        # Update category with the same name and slug as user_2 category
        form_data = {"name": "Category_1", "slug": "category_1"}
        response = self.client.post(reverse("category_update", kwargs={"pk": category.pk}), data=form_data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(ArticleCategoryModel.objects.filter(name="Category_1").count(), 1)
        self.assertEqual(ArticleCategoryModel.objects.count(), 1)
        self.assertFalse(ArticleCategoryModel.objects.filter(name="Another_Category").exists())
        self.assertTrue(self.user.usersettings.categories.filter(name="Category_1").exists())
        self.assertTrue(user_2.usersettings.categories.filter(name="Category_1").exists())

    def test_category_update_change_category_for_user_sources(self):
        # Create source with category_1
        source = Source.objects.create(url="http://example.com/feed/", source_type="RSS")
        UserSource.objects.create(usersettings=self.user.usersettings, source=source, category=self.category)
        self.assertEqual(UserSource.objects.filter(usersettings=self.user.usersettings, source=source).count(), 1)

        # Update category
        form_data = {"name": "Updated_Category", "slug": "updated_category"}
        response = self.client.post(reverse("category_update", kwargs={"pk": self.category.pk}), data=form_data)
        self.assertEqual(response.status_code, 302)

        # Check that user source has updated category
        updated_category = ArticleCategoryModel.objects.get(name="Updated_Category")
        self.assertTrue(UserSource.objects.filter(usersettings=self.user.usersettings, source=source, category=updated_category).exists())
        self.assertEqual(self.user.usersettings.categories.count(), 1)
        self.assertEqual(ArticleCategoryModel.objects.count(), 1)

    def test_category_update_change_categories_for_different_users(self):
        # Create another user
        user_2 = User.objects.create_user(username="user_2", password="User1234")
        self.client.force_login(user_2)

        # Create category for user_2 with the same name and slug as category_1
        user_2.usersettings.categories.add(self.category)
        self.assertEqual(ArticleCategoryModel.objects.count(), 1)
        self.assertEqual(UserCategory.objects.count(), 2)

        # Update category for user_2
        form_data = {"name": "Updated_Category", "slug": "updated_category"}
        response = self.client.post(reverse("category_update", kwargs={"pk": self.category.pk}), data=form_data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(ArticleCategoryModel.objects.count(), 2)
        self.assertEqual(UserCategory.objects.count(), 2)
        self.assertTrue(UserCategory.objects.filter(usersettings=self.user.usersettings, category__name="Category_1").exists())
        self.assertTrue(UserCategory.objects.filter(usersettings=user_2.usersettings, category__name="Updated_Category").exists())

    
class SourceUpdateViewTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="user_1", password="User1234")
        self.client.force_login(self.user)

        # Create category for sources
        self.category = ArticleCategoryModel.objects.create(name="Category_1", slug="category_1")
        self.user.usersettings.categories.add(self.category)

        # Create source
        source = Source.objects.create(url="http://example.com/feed/", source_type="RSS")
        self.user_source = UserSource.objects.create(usersettings=self.user.usersettings, source=source, category=self.category)

    def test_source_update_template(self):
        response = self.client.get(reverse("source_update", kwargs={"pk": self.user_source.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "users/source_update_form.html")

    def test_source_update_empty_form(self):
        form_data = {"url": "", "source_type": "", "category": ""}
        response = self.client.post(reverse("source_update", kwargs={"pk": self.user_source.pk}), data=form_data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Source.objects.filter(pk=self.user_source.source.pk).exists())
        self.assertTrue(UserSource.objects.filter(usersettings=self.user.usersettings, source=self.user_source.source).exists())
        self.assertEqual(Source.objects.count(), 1)
        self.assertEqual(UserSource.objects.count(), 1)

    def test_source_update_valid_form(self):
        form_data = {"url": "http://example.com/updated-feed/", "source_type": "API", "category": self.category.pk, "params": json.dumps({"param1": "value1"})}
        response = self.client.post(reverse("source_update", kwargs={"pk": self.user_source.pk}), data=form_data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Source.objects.filter(url="http://example.com/updated-feed/").exists())
        self.assertTrue(UserSource.objects.filter(usersettings=self.user.usersettings, source__url="http://example.com/updated-feed/").exists())
        self.assertEqual(Source.objects.count(), 1)
        self.assertEqual(UserSource.objects.count(), 1)

    def test_source_update_duplicate_url(self):
        # Create another source with url "http://example.com/another-feed/"
        another_source = Source.objects.create(url="http://example.com/another-feed/", source_type="RSS")
        UserSource.objects.create(usersettings=self.user.usersettings, source=another_source, category=self.category)
        self.assertEqual(Source.objects.filter(url="http://example.com/another-feed/").count(), 1)
        self.assertEqual(self.user.usersettings.sources.filter(url="http://example.com/another-feed/").count(), 1)

        # Try to update source with the same url
        form_data = {"url": "http://example.com/another-feed/", "source_type": "RSS", "category": self.category.pk}
        response = self.client.post(reverse("source_update", kwargs={"pk": self.user_source.pk}), data=form_data)
        self.assertEqual(Source.objects.count(), 2)
        self.assertEqual(UserSource.objects.count(), 2)

