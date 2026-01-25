from django.contrib import admin
from users.models import UserSettings

# Register your models here.

@admin.register(UserSettings)
class UserSettingsAdmin(admin.ModelAdmin):
    list_display = ['user']
    list_display_links = ['user']