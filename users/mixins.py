from django.views.generic import CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from feeds.models import ArticleCategoryModel, Source
from typing import Iterable
from django.contrib.auth.models import User
from django.forms import BaseModelForm


class AddUserSettingsMixin(LoginRequiredMixin, CreateView):
    """Set up UserSettings objects"""
    setting_field = None
    filter_fields = None
    user_unique_fields = None

    def form_valid(self, form):
        #Check if setting_field requirement is defined
        if not self.setting_field:
            raise AttributeError("setting_field is not defined")
        
        setting_value = form.save()
        usersettings = self.request.user.usersettings
        m2m_field = getattr(usersettings, self.setting_field)
        m2m_field.add(setting_value)
        return super().form_valid(form)
    
    def post(self, request, *args, **kwargs):
        #Check if all requirements is defined
        if not self.setting_field:
            raise AttributeError("setting_field is not defined")
        if not self.filter_fields:
            raise AttributeError("filter_fields is not defined")
        
        
        self.object = None

        form = self.get_form()

        filter_params = {field: request.POST.get(field) for field in self.filter_fields}

        existing_obj = self.model.objects.filter(**filter_params).first()
        user_setting = getattr(request.user.usersettings, self.setting_field)

        if existing_obj:
            #check if user already have this object
            if user_setting.filter(**filter_params).exists():
                form.add_error(self.filter_fields[0], "The object is already exists in your list")
                return self.form_invalid(form)
            
            user_setting.add(existing_obj)
            return HttpResponseRedirect(self.success_url)
        
        #check if user try to create new object with same unique field
        if self.user_unique_fields:
            unique_params = [{field: request.POST.get(field)} for field in self.user_unique_fields]
            for param in unique_params:
                if user_setting.filter(**param).exists():
                    form.add_error(self.user_unique_fields[0], f"The {next(iter(param))} should be unique")
                    return self.form_invalid(form)
            
        
        if form.is_valid():
            return self.form_valid(form)
        return self.form_invalid(form)
    

class UpdateUserSettingsMixin(UpdateView):
    setting_field = None
    not_editable_field = None

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()

        if form.is_valid():
            user_objects = getattr(request.user.usersettings, self.setting_field)

            # Check if form have any changes
            if not form.has_changed():
                return HttpResponseRedirect(self.success_url)

            # Check if an identical object already exists
            current_obj = self.object
            self.update_to_existing_obj(form, self.request.user, user_objects, current_obj)
            return HttpResponseRedirect(self.success_url)


        return self.form_invalid(form)

    @classmethod
    def update_to_existing_obj(cls, 
                               form: BaseModelForm,
                               user: User, 
                               user_objects: Iterable[Source] | Iterable[ArticleCategoryModel], 
                               current_obj: Source | ArticleCategoryModel):
        """Update object to existing one"""

        # If object exist - use it
        existing_obj = cls.model.objects.filter(**form.cleaned_data).first()
        if existing_obj:
            result_obj = existing_obj
        # Else, check if there any not editable field and create own one 
        else:
            if cls.not_editable_field:
                field_value = getattr(current_obj, cls.not_editable_field)
                form.cleaned_data[cls.not_editable_field] = field_value
            result_obj = cls.model.objects.create(**form.cleaned_data)
            
        
        # Removing current object from UserSettings field(sources | categories)
        user_objects.remove(current_obj)
        # Add existing object
        user_objects.add(result_obj)

        # If objects type is ArticleCategoryModel - chage category for related sources
        if isinstance(current_obj, ArticleCategoryModel):
            user_sources = getattr(user.usersettings, "sources").all()
            old_category_sources = user_sources.filter(category=current_obj)
            old_category_sources.update(category=result_obj)


        # Remove object from db if no one use it
        if current_obj.user_settings.count() == 0:
            current_obj.delete()


class GetContextDataMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = self.request.user.usersettings.categories.all()
        return context
    