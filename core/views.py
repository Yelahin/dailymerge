from django.shortcuts import render
from feeds.models import ArticleModel
from .utils import menu


# Create your views here.

def home_page(request):
    articles = ArticleModel.objects.all()
    return render(request, 'core/index.html', context={'articles': articles, 'menu': menu})