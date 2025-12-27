from django.shortcuts import render
from feeds.models import ArticleModel, ArticleCategoryModel

# Create your views here.
def news_page(request, slug="world-news"):
    articles = ArticleModel.objects.filter(category__slug=slug)
    categories = ArticleCategoryModel.objects.all()
    return render(request, 'core/index.html', context={'articles': articles, 
                                                       "categories": categories})