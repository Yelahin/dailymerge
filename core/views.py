from django.views.generic.list import ListView
from django.db.models import Q
from feeds.models import ArticleModel
from django.contrib.auth.models import AnonymousUser
from django.shortcuts import redirect
from django.utils import timezone
import datetime

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
        expiring_date = timezone.now() - user.usersettings.article_duration
        qs = ArticleModel.objects.filter(
            source__usersource__usersettings=user.usersettings,
            source__usersource__active=True,
            published__gt=expiring_date,
        )

        #Search bar
        if 'search_bar' in self.request.GET:
            search_terms = self.request.GET['search_bar'].split()
            query = Q()
            for term in search_terms:
                query &= Q(title__icontains=term) | Q(summary__icontains=term)
            queryset = qs.filter(query)
        #Categories
        else:
            queryset = qs.filter(source__usersource__category__slug=slug)
        return queryset.order_by("-published").distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if not isinstance(self.request.user, AnonymousUser):
            usersettings = self.request.user.usersettings
            context['categories'] = usersettings.categories.all()
            context['favorite_article_ids'] = list(usersettings.favorite_articles.values_list('id', flat=True))
        return context

    def dispatch(self, request, *args, **kwargs):
        if not self.kwargs.get('slug'):
            return redirect('filtered_news', self.default_category)
        return super().dispatch(request, *args, **kwargs)
    