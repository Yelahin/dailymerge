from django.http import HttpResponseRedirect, JsonResponse
from django.views.generic import CreateView, TemplateView, ListView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from users.forms import UserCreationForm
from users.mixins import AddUserSettingsMixin, UpdateUserSettingsMixin, GetContextDataMixin
from django.contrib.auth import authenticate, login
from django.contrib.auth.views import PasswordChangeView, PasswordChangeDoneView, PasswordResetView, PasswordResetDoneView, PasswordResetCompleteView, PasswordResetConfirmView, LoginView
from django.contrib.auth.forms import PasswordChangeForm
from feeds.models import Source, ArticleCategoryModel, ArticleModel
from feeds.forms import SourceForm
from django.urls import reverse_lazy

# Create your views here.

class Profile(GetContextDataMixin, LoginRequiredMixin, TemplateView):
    template_name = 'users/profile.html'
    success_url = reverse_lazy('profile')

    def check_delete(self, request, model, field):
        delete_model = f"delete_{model.__name__.lower()}"
        obj_id = request.POST.get(delete_model)
        try:
            obj_to_remove = model.objects.get(id=obj_id)
            settings_field = getattr(request.user.usersettings, field)
            settings_field.remove(obj_to_remove)
            #Check if any other user use this object
            if obj_to_remove.user_settings.count() == 0:
                obj_to_remove.delete()
        except model.DoesNotExist:
            pass
        return HttpResponseRedirect(self.success_url)
                
    
    def post(self, request, *args, **kwargs):
        if 'delete_source' in request.POST:
            return self.check_delete(request, Source, "sources")
        if 'delete_articlecategorymodel' in request.POST:
            return self.check_delete(request, ArticleCategoryModel, "categories")
        

    def get_context_data(self, **kwargs):
        usersettings = self.request.user.usersettings
        context = super().get_context_data(**kwargs)
        context['sources'] = usersettings.sources.all()
        return context


class FavoriteArticles(LoginRequiredMixin, GetContextDataMixin, ListView):
    model = ArticleModel
    template_name = "users/favorite.html"
    context_object_name = "articles"

    def get_queryset(self):
        print("FavoriteArticles view is called")  # Debug
        user = self.request.user
        queryset = user.usersettings.favorite_articles.all()
        return queryset


class ToggleFavorite(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        article_id = kwargs.get('pk')
        try:
            article = ArticleModel.objects.get(id=article_id)
            user_settings = request.user.usersettings
            if article in user_settings.favorite_articles.all():
                user_settings.favorite_articles.remove(article)
                is_favorite = False
            else:
                user_settings.favorite_articles.add(article)
                is_favorite = True
            return JsonResponse({'status': 'success', 'is_favorite': is_favorite})
        except ArticleModel.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Article not found'}, status=404)


class SourceCreate(GetContextDataMixin, AddUserSettingsMixin):
    model = Source
    form_class = SourceForm
    template_name = "users/source_create_form.html"
    success_url = reverse_lazy('profile')
    setting_field = 'sources'
    filter_fields = ['url', 'category']

    def get_form(self, form_class=None):
        """Pass usersettings to form class"""
        form_class = self.get_form_class()
        user_settings = self.request.user.usersettings
        return form_class(**self.get_form_kwargs(), user_settings=user_settings)

        
class SourceUpdate(GetContextDataMixin, LoginRequiredMixin, UpdateUserSettingsMixin):
    model = Source
    form_class = SourceForm
    template_name = "users/source_update_form.html"
    success_url = reverse_lazy('profile')
    setting_field = "sources"

    def get_form(self, form_class=None):
        form_class = self.get_form_class()
        user_settings = self.request.user.usersettings
        return form_class(**self.get_form_kwargs(), user_settings=user_settings)


class CategoryCreate(GetContextDataMixin, AddUserSettingsMixin):
    model = ArticleCategoryModel
    template_name = "users/category_create_form.html"
    fields = ['name', 'slug']
    success_url = reverse_lazy('profile')
    setting_field = 'categories'
    filter_fields = ['name', 'slug']
    user_unique_fields = ['name', 'slug']


class CategoryUpdate(GetContextDataMixin, LoginRequiredMixin, UpdateUserSettingsMixin):
    model = ArticleCategoryModel
    template_name = "users/category_update_form.html"
    fields = ['name']
    success_url = reverse_lazy('profile')
    setting_field = "categories"
    not_editable_field = "slug"
    

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


class PasswordChange(GetContextDataMixin, PasswordChangeView):
    form_class = PasswordChangeForm
    success_url = reverse_lazy("password_change_done")
    template_name = "users/pwd_change.html"


class PasswordChangeDone(GetContextDataMixin, PasswordChangeDoneView):
    template_name = "users/pwd_change_done.html"


class PasswordReset(PasswordResetView):
    template_name = "users/pwd_reset_form.html"


class PasswordResetDone(PasswordResetDoneView):
    template_name = "users/pwd_reset_done.html"


class PasswordResetConfirm(PasswordResetConfirmView):   
    template_name = "users/pwd_reset_confirm.html"


class PasswordResetComplete(PasswordResetCompleteView):
    template_name = "users/pwd_reset_complete.html"
