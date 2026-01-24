from django.views.generic import CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.db import models

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
            user_setting = getattr(request.user.usersettings, self.setting_field)
            
            # Check if an identical object already exists
            existing_obj = self.model.objects.filter(**form.cleaned_data).first()
            if existing_obj:
                # If it exists, delete current object and use the existing one
                current_obj = self.get_object()
                user_setting.remove(current_obj)
                if current_obj.user_settings.count() == 0:
                    current_obj.delete()
                user_setting.add(existing_obj)
                return HttpResponseRedirect(self.success_url)
            
            obj = self.get_object()
            # If this object is shared by multiple users, create a new copy
            if obj.user_settings.count() > 1:
                if self.not_editable_field:
                    field_value = getattr(obj, self.not_editable_field)
                    form.changed_data[self.not_editable_field] = field_value
                
                new_obj = self.model.objects.create(**form.cleaned_data)
                
                # Replace the old object with the new one for this user
                user_setting.remove(obj)
                user_setting.add(new_obj)
                return HttpResponseRedirect(self.success_url)
            else:
                return self.form_valid(form)

        return self.form_invalid(form)
    
