from django.shortcuts import render
from .models import ArticleModel

# Create your views here.
def feeds(request):
    data = ArticleModel.objects.all().order_by('published')
    return render(request, 'feeds/feeds.html', context={'data': data})