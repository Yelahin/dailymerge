from django.views.generic import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect

class AddUserSettingsMixin(LoginRequiredMixin, CreateView):
    """Set up UserSettings objects"""
    setting_field = None
    filter_field = None

    def form_valid(self, form):
        if not self.setting_field:
            raise AttributeError("setting_field is not defined")
        setting_value = form.save()
        usersettings = self.request.user.usersettings
        m2m_field = getattr(usersettings, self.setting_field)
        m2m_field.add(setting_value)
        return super().form_valid(form)
    
    def post(self, request, *args, **kwargs):
        if not self.setting_field:
            raise AttributeError("setting_field is not defined")
        if not self.filter_field:
            raise AttributeError("filter_field is not defined")
        
        
        self.object = None

        form = self.get_form()
        filter_value = request.POST.get(self.filter_field)
        user_setting = getattr(request.user.usersettings, self.setting_field)
        existing_obj = self.model.objects.filter(**{self.filter_field: filter_value}).first()
        if existing_obj:
            if user_setting.filter(**{self.filter_field: filter_value}).exists():
                form.add_error(self.filter_field, "The object is already exists in your list")
                return self.form_invalid(form)
            user_setting.add(existing_obj)
            return HttpResponseRedirect(self.success_url)
        
        if form.is_valid():
            return self.form_valid(form)
        return self.form_invalid(form)
    