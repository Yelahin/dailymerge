from django.db import models
from django.contrib.auth.models import User
from feeds.models import Source


# Create your models here.

class UserSettings(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    source = models.ManyToManyField(Source, blank=True)
    