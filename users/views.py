from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.generic import CreateView
from users.forms import UserCreationForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.views import PasswordChangeView, PasswordChangeDoneView
from django.contrib.auth.forms import PasswordChangeForm
from django.urls import reverse_lazy

# Create your views here.

@login_required
def profile(request):
    return render(request, 'registration/profile.html')

class SignUp(CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy('news')
    template_name = 'registration/signup.html' 

    def form_valid(self, form):
        response = super().form_valid(form)
        user = authenticate(username=form.cleaned_data['username'],
                            password=form.cleaned_data['password1'])
        login(self.request, user)
        return response

  
class PasswordChange(PasswordChangeView):
    form_class = PasswordChangeForm
    success_url = reverse_lazy("password_change_done")
    template_name = "registration/pwd_change.html"

class PasswordChangeDone(PasswordChangeDoneView):
    template_name = "registration/pwd_change_done.html"