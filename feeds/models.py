from django.db import models

# Create your models here.

class ArticleModel(models.Model):
    title = models.CharField(max_length=500)
    link = models.URLField(unique=True)
    published = models.DateTimeField()
    summary = models.TextField()
    image_url = models.URLField(max_length=500)

    def __str__(self):
        return self.title