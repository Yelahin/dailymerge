from django.db import models

# Create your models here.

class ArticleCategoryModel(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class ArticleModel(models.Model):
    title = models.CharField(max_length=500)
    link = models.URLField(unique=True)
    published = models.DateTimeField()
    summary = models.TextField()
    image_url = models.URLField(max_length=500)
    category = models.ForeignKey(ArticleCategoryModel, on_delete=models.CASCADE)

    def __str__(self):
        return self.title
