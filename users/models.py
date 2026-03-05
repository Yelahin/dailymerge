from django.db import models
from django.contrib.auth.models import User
from feeds.models import Source, ArticleCategoryModel, ArticleModel
from django.db.models.signals import post_save
from django.dispatch import receiver
import datetime



# Create your models here.

class UserSource(models.Model):
    usersettings = models.ForeignKey("UserSettings", on_delete=models.CASCADE)
    source = models.ForeignKey(Source, on_delete=models.CASCADE)
    category = models.ForeignKey(ArticleCategoryModel, on_delete=models.CASCADE, related_name="sources")
    active = models.BooleanField(default=True)

    class Meta:
        unique_together = ('usersettings', 'source', 'category')


class UserCategory(models.Model):
    usersettings = models.ForeignKey("UserSettings", on_delete=models.CASCADE)
    category = models.ForeignKey(ArticleCategoryModel, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('usersettings', 'category')


class UserSettings(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    sources = models.ManyToManyField(Source, through=UserSource, blank=True)
    categories = models.ManyToManyField(ArticleCategoryModel, through=UserCategory, blank=True)
    article_duration = models.DurationField(default=datetime.timedelta(days=7))
    favorite_articles = models.ManyToManyField(ArticleModel, blank=True)
    

@receiver(post_save, sender=User)
def create_user_settings(sender, instance, created, **kwargs):
    if created:
        UserSettings.objects.get_or_create(user=instance)
