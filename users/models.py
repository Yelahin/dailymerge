from django.db import models
from django.contrib.auth.models import User
from feeds.models import Source, ArticleCategoryModel, ArticleModel
from django.db.models.signals import post_save
from django.dispatch import receiver


# Create your models here.

class UserSettings(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    sources = models.ManyToManyField(Source, blank=True, related_name="user_settings")
    categories = models.ManyToManyField(ArticleCategoryModel, blank=True, related_name="user_settings")
    favorite_articles = models.ManyToManyField(ArticleModel, blank=True, related_name="user_settings")
    

@receiver(post_save, sender=User)
def create_user_settings(sender, instance, created, **kwargs):
    if created:
        UserSettings.objects.get_or_create(user=instance)