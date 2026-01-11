from django.contrib import admin
from feeds.models import ArticleModel, ArticleCategoryModel

# Register your models here.

@admin.register(ArticleModel)
class ArticleModelAdmin(admin.ModelAdmin):
    list_display = ['title', 'published', 'category']
    list_display_links = ['title']
    ordering = ['published']


@admin.register(ArticleCategoryModel)
class ArticleCategoryModelAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    list_display_links = ['name', 'slug']
    ordering = ['slug']