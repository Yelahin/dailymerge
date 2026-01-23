from django.http import HttpResponseRedirect
from django.views.generic import CreateView, TemplateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.views.generic.edit import FormMixin
from users.forms import UserCreationForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.views import PasswordChangeView, PasswordChangeDoneView, PasswordResetView, PasswordResetDoneView, PasswordResetCompleteView, PasswordResetConfirmView
from django.contrib.auth.forms import PasswordChangeForm
from feeds.forms import SourceForm
from feeds.models import Source
from django.urls import reverse_lazy

# Create your views here.

class Profile(FormMixin, LoginRequiredMixin, TemplateView):
    form_class = SourceForm
    template_name = 'users/profile.html'
    success_url = reverse_lazy('profile')

    def form_valid(self, form):
        source = form.save()
        user = self.request.user.usersettings
        user.source.add(source)
        return HttpResponseRedirect(self.get_success_url())
    
    def post(self, request, *args, **kwargs):
        if 'delete_source' in request.POST:
            source_id = request.POST.get('delete_source')
            try:
                source_to_remove = Source.objects.get(id=source_id)
                request.user.usersettings.source.remove(source_to_remove)
            except Source.DoesNotExist:
                pass
            return HttpResponseRedirect(self.get_success_url())

        # Check if source with this URL already exists to avoid unique constraint error
        if 'url' in request.POST:
            url = request.POST.get('url')
            existing_source = Source.objects.filter(url=url).first()
            if existing_source:
                # If source exists, just add it to the user's settings
                request.user.usersettings.source.add(existing_source)
                return HttpResponseRedirect(self.get_success_url())

        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        return self.form_invalid(form)

    def get_context_data(self, **kwargs):
        user = self.request.user
        context = super().get_context_data(**kwargs)
        context['sources'] = user.usersettings.source.all()
        return context


class SignUp(CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy('news')
    template_name = 'users/signup.html' 

    def form_valid(self, form):
        response = super().form_valid(form)
        user = authenticate(username=form.cleaned_data['username'],
                            password=form.cleaned_data['password1'])
        login(self.request, user)
        return response


class Login(LoginView):
    template_name = "users/login.html"


class PasswordChange(PasswordChangeView):
    form_class = PasswordChangeForm
    success_url = reverse_lazy("password_change_done")
    template_name = "users/pwd_change.html"


class PasswordChangeDone(PasswordChangeDoneView):
    template_name = "users/pwd_change_done.html"


class PasswordReset(PasswordResetView):
    template_name = "users/pwd_reset_form.html"


class PasswordResetDone(PasswordResetDoneView):
    template_name = "users/pwd_reset_done.html"


class PasswordResetConfirm(PasswordResetConfirmView):   
    template_name = "users/pwd_reset_confirm.html"


class PasswordResetComplete(PasswordResetCompleteView):
    template_name = "users/pwd_reset_complete.html"