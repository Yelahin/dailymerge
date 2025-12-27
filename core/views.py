from django.shortcuts import render
from feeds.models import ArticleModel, ArticleCategoryModel

# Create your views here.
def news_page(request):
    articles = ArticleModel.objects.all()
    categories = ArticleCategoryModel.objects.all()
    return render(request, 'core/index.html', context={'articles': articles, 
                                                       "categories": categories})