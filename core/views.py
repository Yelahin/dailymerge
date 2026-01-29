from django.views.generic.list import ListView
from django.db.models import Q
from feeds.models import ArticleModel
from django.contrib.auth.models import AnonymousUser
from django.shortcuts import redirect
from django.utils import timezone

# Create your views here.

class ArticleListView(ListView):
    model = ArticleModel
    template_name = 'core/index.html'
    context_object_name = "articles"
    ordering = 'published'

    def get_queryset(self):
        user = self.request.user

        # Return None if user not authenticated 
        if isinstance(user, AnonymousUser):
            return None

        # Return users articles that active and pass expiring date
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
                # Add articles that use terms in fields below
                query &= (Q(title__icontains=term) | 
                          Q(summary__icontains=term) | 
                          Q(source__usersource__category__name=term) |
                          Q(source__usersource__category__slug=term))
            queryset = qs.filter(query)
        #Categories
        else:
            # Return category by slug
            slug = self.kwargs.get('slug')
            if slug:
                queryset = qs.filter(source__usersource__category__slug=slug, source__usersource__usersettings=user.usersettings)
            # Return users favorite articles if there is no slug
            else:
                query = user.usersettings.favorite_articles.all()

        return queryset.order_by("-published").distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if not isinstance(self.request.user, AnonymousUser):
            usersettings = self.request.user.usersettings
            context['categories'] = usersettings.categories.all()
            context['favorite_article_ids'] = list(usersettings.favorite_articles.values_list('id', flat=True))
        return context

    def dispatch(self, request, *args, **kwargs):
        # Redirect user to login page if user isn't logged in
        if isinstance(self.request.user, AnonymousUser):
            return redirect('login')
        
        # Redirect user to page with articles of chosen category
        if self.kwargs.get('slug'):
            return super().dispatch(request, *args, **kwargs)
        
        # Redirect logged user to page with favorite articles
        else:
            return redirect('favorite')
    