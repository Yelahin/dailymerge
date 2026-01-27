from django.db import models

# Create your models here.

class ArticleCategoryModel(models.Model):
    name = models.CharField(max_length=100, unique=False)
    slug = models.SlugField(unique=False)

    def __str__(self):
        return self.name


class Source(models.Model):
    class SourceType(models.TextChoices):
        RSS = "RSS", "RSS"
        API = "API", "API"

    url = models.URLField(max_length=500)
    source_type = models.CharField(max_length=10, choices=SourceType.choices)

    class Meta:
        unique_together = ('url', 'source_type')


class ArticleModel(models.Model):
    title = models.CharField(max_length=500)
    link = models.URLField(unique=True, max_length=350)
    published = models.DateTimeField()
    summary = models.TextField()
    image_url = models.URLField(max_length=500)
    source = models.ForeignKey(Source, on_delete=models.CASCADE, related_name="articles")
    