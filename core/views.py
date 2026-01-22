from django.views.generic.list import ListView
from django.db.models import Q
from feeds.models import ArticleModel, ArticleCategoryModel
from django.contrib.auth.models import AnonymousUser
from django.core.cache import cache
from django.shortcuts import redirect

# Create your views here.

class ArticleListView(ListView):
    model = ArticleModel
    template_name = 'core/index.html'
    context_object_name = "articles"
    ordering = 'published'
    default_category = 'world-news'

    def get_queryset(self):
        user = self.request.user
        if isinstance(user, AnonymousUser):
            return None
        slug = self.kwargs.get('slug', self.default_category)
        qs = ArticleModel.objects.filter(source__in=user.usersettings.source.all())

        #Search bar
        if 'search_bar' in self.request.GET:
            search_terms = self.request.GET['search_bar'].split()
            query = Q()
            for term in search_terms:
                query &= Q(title__icontains=term) | Q(summary__icontains=term)
            queryset = qs.filter(query)
        #Categories
        else:
            #Caching for default category
            if slug == self.default_category:
                queryset = cache.get_or_set(
                    f'article_source_category_{self.request.user.id}',
                    qs.filter(source__category__slug=slug),
                    30,
                )
            #Not default category
            else:
                queryset = qs.filter(source__category__slug=slug)
        return queryset.order_by("-published")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = ArticleCategoryModel.objects.all()
        return context

    def dispatch(self, request, *args, **kwargs):
        if not self.kwargs.get('slug'):
            return redirect('filtered_news', self.default_category)
        return super().dispatch(request, *args, **kwargs)
    