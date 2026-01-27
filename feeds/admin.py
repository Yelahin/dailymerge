from django.contrib import admin
from feeds.models import ArticleModel, ArticleCategoryModel, Source

# Register your models here.

@admin.register(ArticleModel)
class ArticleModelAdmin(admin.ModelAdmin):
    list_display = ['title', 'published']
    list_display_links = ['title']
    ordering = ['published']


@admin.register(ArticleCategoryModel)
class ArticleCategoryModelAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    list_display_links = ['name', 'slug']
    ordering = ['slug']


class ActivateMixin:
    actions = ['activate_feeds', 'diactivate_feeds']

    @admin.action(description="Activate feeds")
    def activate_feeds(self, request, queryset):
        queryset.update(active=True)

    @admin.action(description="Diactivate feeds")
    def diactivate_feeds(self, request, queryset):
        queryset.update(active=False)


@admin.register(Source)
class SourceAdmin(admin.ModelAdmin):
    list_display = ['url']
    list_display_links = ['url']