from django.http import HttpResponseRedirect, JsonResponse
from django.views.generic import CreateView, UpdateView, TemplateView, ListView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from users.forms import UserCreationForm
from users.mixins import GetContextDataMixin
from django.contrib.auth import authenticate, login
from django.contrib.auth.views import PasswordChangeView, PasswordChangeDoneView, PasswordResetView, PasswordResetDoneView, PasswordResetCompleteView, PasswordResetConfirmView, LoginView
from django.contrib.auth.forms import PasswordChangeForm
from feeds.models import Source, ArticleCategoryModel, ArticleModel
from feeds.forms import SourceForm
from django.urls import reverse_lazy
from users.models import UserSource, UserCategory

# Create your views here.

class Profile(GetContextDataMixin, LoginRequiredMixin, TemplateView):
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
        if 'delete_source' in request.POST:
            return self.check_delete(request, Source)
        if 'delete_articlecategorymodel' in request.POST:
            return self.check_delete(request, ArticleCategoryModel)
        
    def get_context_data(self, **kwargs):
        usersettings = self.request.user.usersettings
        sources = usersettings.sources.all()
        context = super().get_context_data(**kwargs)
        context['sources'] = UserSource.objects.filter(source__in=sources, usersettings=usersettings).distinct()
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


class UserSourceCreateView(GetContextDataMixin, LoginRequiredMixin, CreateView):
    model = UserSource
    form_class = SourceForm
    template_name = "users/source_create_form.html"
    success_url = reverse_lazy('profile')

    def get_form(self, form_class=None):
        """Pass usersettings to form class"""
        form_class = self.get_form_class()
        usersettings = self.request.user.usersettings
        return form_class(**self.get_form_kwargs(), usersettings=usersettings)
    
    def form_valid(self, form):
        usersettings = self.request.user.usersettings

        if UserSource.objects.filter(
            usersettings=usersettings,
            source=Source.objects.filter(url=form.cleaned_data['url'], source_type=form.cleaned_data['source_type']).first(),
            category=form.cleaned_data['category']
        ).exists():
            form.add_error('url', "You already have this source with same: url, source_type, category")
            return self.form_invalid(form)

        self.object = form.save()
        return HttpResponseRedirect(self.success_url)
    
    """
    def post(self, request, *args, **kwargs):
        form = self.get_form()

        if form.is_valid():
            usersettings = request.user.usersettings
            filter_data = form.cleaned_data.copy()
            filter_data['source__url'] = filter_data.pop('url')
            if UserSource.objects.filter(
                usersettings=usersettings,
                source=Source.objects.get(url=form.cleaned_data['url'], source_type=form.cleaned_data['source_type']),
                category=form.cleaned_data['category']
                ).exists():
                return self.form_invalid(form)
            return self.form_valid(form)
        else:
            return self.form_invalid(form)
    """

class UserSourceUpdateView(GetContextDataMixin, LoginRequiredMixin, UpdateView):
    model = UserSource
    form_class = SourceForm
    template_name = "users/source_update_form.html"
    success_url = reverse_lazy('profile')

    def get_form(self, form_class=None):
        # Get the user settings 
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
                'source_type': object.source.source_type
            },
            **kwargs
        )
        return form

    def form_valid(self, form):
        user_source = form.save(commit=False)

        source, created = Source.objects.get_or_create(
            url=form.cleaned_data['url'],
            source_type=form.cleaned_data['source_type']
        )

        user_source.source = source
        user_source.save()

        return super().form_valid(form)


class CategoryCreateView(GetContextDataMixin, LoginRequiredMixin, CreateView):
    model = ArticleCategoryModel
    template_name = "users/category_create_form.html"
    fields = ['name', 'slug']
    success_url = reverse_lazy('profile')

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        
        if form.is_valid():
            usersettings = request.user.usersettings
            
            # Get or create category for usersettings
            self.object, created = self.model.objects.get_or_create(**form.cleaned_data)

            # Check if user try to create object with not unique fields
            for field in self.fields:
                if usersettings.categories.filter(**{field: form.cleaned_data[field]}).exists():
                    form.add_error(field, "You already have this object")
                    return self.form_invalid(form)

            # Add category
            usersettings.categories.add(self.object)
            
            return HttpResponseRedirect(self.success_url)
        else:
            return self.form_invalid(form)


class CategoryUpdate(GetContextDataMixin, LoginRequiredMixin, UpdateView):
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
                
            form.cleaned_data['slug'] = self.object.slug
            updated_category, created = ArticleCategoryModel.objects.get_or_create(**form.cleaned_data)

            usersettings.categories.add(updated_category)
            UserSource.objects.filter(category=self.object, usersettings=usersettings).update(category=updated_category)
            usersettings.categories.remove(self.object)

            if not self.object.usersettings_set.exists():
                self.object.delete()
            return HttpResponseRedirect(self.success_url)
        else:
            return self.form_invalid(form)
        

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
