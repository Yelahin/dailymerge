from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy


class LoginRequiredMixin(LoginRequiredMixin):
    login_url = reverse_lazy('login')


class GetContextDataMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = self.request.user.usersettings.categories.all()
        return context
    