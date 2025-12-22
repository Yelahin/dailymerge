from django.shortcuts import render
from .models import ArticleModel
from django.utils import timezone

# Create your views here.
def feeds(request):
    data = ArticleModel.objects.all()
    return render(request, 'feeds/feeds.html', context={'data': data})