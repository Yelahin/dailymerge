from django.views.generic.list import ListView
from django.db.models import Q
from feeds.models import ArticleModel, ArticleCategoryModel

# Create your views here.


class ArticleListView(ListView):
    model = ArticleModel
    template_name = 'core/index.html'
    context_object_name = "articles"
    ordering = 'published'

    def get_queryset(self):
        if 'search-bar' in self.request.GET:
            search_terms = self.request.GET['search-bar'].split()
            query = Q()
            for term in search_terms:
                query &= Q(title__icontains=term) | Q(summary__icontains=term)
            queryset = ArticleModel.objects.filter(query)
        else:
            slug = self.kwargs.get('slug', 'world-news')
            queryset = ArticleModel.objects.filter(category__slug=slug)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = ArticleCategoryModel.objects.all()
        return context
