from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy


class LoginRequiredMixin(LoginRequiredMixin):
    login_url = reverse_lazy('login')


class GetContextDataMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        usersettings = self.request.user.usersettings
        context['categories'] = usersettings.categories.all()
        context['favorite_article_ids'] = list(usersettings.favorite_articles.values_list('id', flat=True))
        return context
    