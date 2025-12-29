from django.db import models
from django.template.defaultfilters import slugify

# Create your models here.

class ArticleCategoryModel(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField()

    def save(self, *args, **kwargs):
        if not self.id:
            self.slug = slugify(self.name)
        
        super(ArticleCategoryModel, self).save(*args, **kwargs)

    def __str__(self):
        return self.name

class ArticleModel(models.Model):
    title = models.CharField(max_length=500)
    link = models.URLField(unique=True, max_length=350)
    published = models.DateTimeField()
    summary = models.TextField()
    image_url = models.URLField(max_length=500)
    category = models.ForeignKey(ArticleCategoryModel, on_delete=models.CASCADE)

    def __str__(self):
        return self.title
