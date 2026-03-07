from django.utils import timezone
from django.http import HttpResponseRedirect, JsonResponse
from django.views.generic import CreateView, UpdateView, TemplateView, ListView, View
from users.mixins import LoginRequiredMixin
from users.forms import UserCreationForm, UserArticleDurationForm
from users.mixins import GetContextDataMixin
from django.contrib.auth import authenticate, login
from django.contrib.auth.views import PasswordChangeView, PasswordChangeDoneView, PasswordResetView, PasswordResetDoneView, PasswordResetCompleteView, PasswordResetConfirmView, LoginView
from django.contrib.auth.forms import PasswordChangeForm
from feeds.models import Source, ArticleCategoryModel, ArticleModel
from feeds.forms import SourceForm
from django.urls import reverse_lazy
from django.shortcuts import render
from users.models import UserSource, UserCategory

# Create your views here.

class HomePageListView(GetContextDataMixin, LoginRequiredMixin, ListView):
    model = ArticleModel
    context_object_name = "articles"
    ordering = "published"
    template_name = 'users/home_page.html'

    def get_queryset(self):
        user = self.request.user

        # Return users articles that active and pass expiring date
        expiring_date = timezone.now() - user.usersettings.article_duration
        queryset = ArticleModel.objects.filter(
            source__usersource__usersettings=user.usersettings,
            source__usersource__active=True,
            published__gt=expiring_date,
        ).order_by("-published").distinct()

        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_sources = UserSource.objects.filter(usersettings=self.request.user.usersettings).select_related('category')
        source_category_map = {user_source.source.id: user_source.category for user_source in user_sources}
        context['source_category_map'] = source_category_map
        return context


class ProfileView(GetContextDataMixin, LoginRequiredMixin, TemplateView):
    template_name = 'users/profile.html'
    success_url = reverse_lazy('profile')

    def check_delete(self, request, model):
        # Get usersettings
        usersettings = request.user.usersettings

        #Get removing object id
        delete_model = f"delete_{model.__name__.lower()}"
        obj_id = request.POST.get(delete_model)

        try:
            obj_to_remove = model.objects.get(id=obj_id)

            if model == Source:
                # Remove source from user
                UserSource.objects.filter(
                    usersettings=usersettings,
                    source=obj_to_remove
                ).delete()

                # Check if any other user using this source
                still_used = UserSource.objects.filter(source=obj_to_remove).exists()

            elif model == ArticleCategoryModel:
                # Get all users sources using removing category
                user_sources_to_delete = UserSource.objects.filter(
                    usersettings=usersettings,
                    category=obj_to_remove
                )

                # Get ids of sources used in users sources
                sources_ids = list(user_sources_to_delete.values_list("source", flat=True))

                # Delete users sources using removing category
                user_sources_to_delete.delete()

                # Delete all unused sources
                for source_id in sources_ids:
                    if not UserSource.objects.filter(source=source_id).exists():
                        Source.objects.filter(id=source_id).delete()

                UserCategory.objects.filter(
                    usersettings=usersettings,
                    category=obj_to_remove
                ).delete()

                # Check if any other user using this category
                still_used = UserCategory.objects.filter(category=obj_to_remove).exists()
                
            # If other users don't use the object - remove it!
            if not still_used:
                obj_to_remove.delete()

        except model.DoesNotExist:
            pass
        return HttpResponseRedirect(self.success_url)
                    
    def post(self, request, *args, **kwargs):
        # Models used in delete forms
        models_to_delete = [Source, ArticleCategoryModel]

        for model in models_to_delete:
            model_delete = f"delete_{model.__name__.lower()}"
            if model_delete in request.POST:
                return self.check_delete(request, model)
        
        # Check if user change article duration form
        if any(field in request.POST for field in ['days', 'hours', 'minutes']):
            usersettings = request.user.usersettings
            form = UserArticleDurationForm(request.POST, instance=usersettings)
            if form.is_valid():
                form.save()
                return HttpResponseRedirect(self.success_url)

    def get_context_data(self, **kwargs):
        usersettings = self.request.user.usersettings
        sources = usersettings.sources.all()
        context = super().get_context_data(**kwargs)
        context['sources'] = UserSource.objects.filter(source__in=sources, usersettings=usersettings).distinct()
        context['settings_form'] = UserArticleDurationForm(instance=usersettings)
        return context


class FavoriteArticlesView(GetContextDataMixin, LoginRequiredMixin, ListView):
    model = ArticleModel
    template_name = "users/favorite.html"
    context_object_name = "articles"

    def get_queryset(self):
        user = self.request.user
        queryset = user.usersettings.favorite_articles.all()
        return queryset


class ToggleFavoriteView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        article_id = kwargs.get('pk')
        try:
            # Get toggled article
            article = ArticleModel.objects.get(id=article_id)
            user_settings = request.user.usersettings

            # Remove article if user toggled favorite article
            if article in user_settings.favorite_articles.all():
                user_settings.favorite_articles.remove(article)
                is_favorite = False

            # Add article to user favorites
            else:
                user_settings.favorite_articles.add(article)
                is_favorite = True
            
            # Return result to JS
            return JsonResponse({'status': 'success', 'is_favorite': is_favorite})
        except ArticleModel.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Article not found'}, status=404)


class UserSourceCreateView(GetContextDataMixin, LoginRequiredMixin, CreateView):
    model = UserSource
    form_class = SourceForm
    template_name = "users/source_create_form.html"
    success_url = reverse_lazy('pending')

    def get_form(self, form_class=None):
        """Pass usersettings to form class"""
        form_class = self.get_form_class()
        usersettings = self.request.user.usersettings
        return form_class(**self.get_form_kwargs(), usersettings=usersettings)
    
    def form_valid(self, form):
        usersettings = self.request.user.usersettings

        # Check if user have source with same url and category
        if UserSource.objects.filter(
            usersettings=usersettings,
            source=Source.objects.filter(url=form.cleaned_data['url']).first(),
            category=form.cleaned_data['category']
        ).exists():
            form.add_error('url', "You already have this source with same: url, category")
            return self.form_invalid(form)

        self.object = form.save()
        return HttpResponseRedirect(self.success_url)


class UserSourceUpdateView(GetContextDataMixin, LoginRequiredMixin, UpdateView):
    model = UserSource
    form_class = SourceForm
    template_name = "users/source_update_form.html"
    success_url = reverse_lazy('pending')

    def get_form(self, form_class=None):
        usersettings = self.request.user.usersettings

        # Get user input
        kwargs = {}
        if self.request.method in ("POST", "PUT"):
            kwargs.update({
                "data": self.request.POST,
                "files": self.request.FILES
            })

        # Get object being edited    
        object = self.get_object()

        # Return edited form
        form = SourceForm(
            instance=object,
            usersettings=usersettings, 
            initial={
                'url': object.source.url,
            },
            **kwargs
        )
        return form

    def form_valid(self, form): 
        if form.has_changed():
            old_source = self.get_object().source

            # Get user input
            new_user_source = form.save(commit=False)

            if old_source != new_user_source.source:
                # Get or create source same to user input
                source, created = Source.objects.get_or_create(
                    url=new_user_source.source.url,
                )

                new_user_source.source = source

                if UserSource.objects.filter(source=old_source).count() <= 1:
                    old_source.delete()

            new_user_source.save()

        return super().form_valid(form)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()

        if form.is_valid():
            if UserSource.objects.filter(
                usersettings=request.user.usersettings,
                source__url=form.cleaned_data['url'],
            ).exclude(id=self.object.id).exists():
                form.add_error('url', "You already have this source with same: url category")
                return self.form_invalid(form)
            return self.form_valid(form)
        else:
            return self.form_invalid(form)


class CategoryCreateView(GetContextDataMixin, LoginRequiredMixin, CreateView):
    model = ArticleCategoryModel
    template_name = "users/category_create_form.html"
    fields = ['name', 'slug']
    success_url = reverse_lazy('profile')

    def post(self, request, *args, **kwargs):
        form = self.get_form()

        self.object = None
        
        if form.is_valid():
            usersettings = request.user.usersettings

            # Check if user try to create object and unique fields don't pass
            for field in self.fields:
                if usersettings.categories.filter(**{field: form.cleaned_data[field]}).exists():
                    form.add_error(field, "You already have this object")
                    return self.form_invalid(form)
                
            # Get or create category for user
            self.object, created = self.model.objects.get_or_create(**form.cleaned_data)

            # Add category
            usersettings.categories.add(self.object)
            
            return HttpResponseRedirect(self.success_url)
        else:
            return self.form_invalid(form)


class CategoryUpdateView(GetContextDataMixin, LoginRequiredMixin, UpdateView):
    model = ArticleCategoryModel
    template_name = "users/category_update_form.html"
    fields = ['name']
    success_url = reverse_lazy('profile')
    
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()

        if form.is_valid():
            usersettings = request.user.usersettings

            # Check if user didn't change form
            if not form.has_changed():
                return HttpResponseRedirect(self.success_url)
            
            # Check if user try to update object fields to existing ones
            for field in self.fields:
                param = {field: getattr(self.object, field)}
                if usersettings.categories.filter(**param).exists():
                    form.add_error(field, f"You already have category with this {field}")
                    return self.form_invalid(form)
                
            # Add not editable field(slug)
            form.cleaned_data['slug'] = self.object.slug
            updated_category, created = ArticleCategoryModel.objects.get_or_create(**form.cleaned_data)

            # Add edited category to user
            usersettings.categories.add(updated_category)

            # Update category in user sources with edited category
            UserSource.objects.filter(category=self.object, usersettings=usersettings).update(category=updated_category)

            # Remove old category from user
            usersettings.categories.remove(self.object)

            # If other users don't use old category - delete it!
            if not self.object.usersettings_set.exists():
                self.object.delete()
            return HttpResponseRedirect(self.success_url)
        else:
            return self.form_invalid(form)
        

class PendingView(GetContextDataMixin, LoginRequiredMixin, TemplateView):
    template_name = "users/pending.html"


class SignUpView(CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy('news')
    template_name = 'users/signup.html' 

    def form_valid(self, form):
        # Make user login after registration
        response = super().form_valid(form)
        user = authenticate(username=form.cleaned_data['username'],
                            password=form.cleaned_data['password1'])
        login(self.request, user)
        return response


class LoginView(LoginView):
    template_name = "users/login.html"


class PasswordChangeView(GetContextDataMixin, PasswordChangeView):
    form_class = PasswordChangeForm
    success_url = reverse_lazy("password_change_done")
    template_name = "users/pwd_change.html"


class PasswordChangeDoneView(GetContextDataMixin, PasswordChangeDoneView):
    template_name = "users/pwd_change_done.html"


class PasswordResetView(PasswordResetView):
    template_name = "users/pwd_reset_form.html"


class PasswordResetDoneView(PasswordResetDoneView):
    template_name = "users/pwd_reset_done.html"


class PasswordResetConfirmView(PasswordResetConfirmView):   
    template_name = "users/pwd_reset_confirm.html"


class PasswordResetCompleteView(PasswordResetCompleteView):
    template_name = "users/pwd_reset_complete.html"
