from django.shortcuts import render
from django.views.generic.list import ListView
from feeds.models import ArticleModel, ArticleCategoryModel

# Create your views here.


class ArticleListView(ListView):
    model = ArticleModel
    template_name = 'core/index.html'
    context_object_name = "articles"
    ordering = 'published'

    def get_queryset(self):
        slug = self.kwargs.get('slug', 'world-news')
        return ArticleModel.objects.filter(category__slug=slug)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = ArticleCategoryModel.objects.all()
        return context
