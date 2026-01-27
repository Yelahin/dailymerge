from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from users.models import UserSettings
import datetime


class UserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

    def save(self, commit=True):
        user = super(UserCreationForm, self).save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user


class UserSettingsForm(forms.ModelForm):
    days = forms.IntegerField(min_value=0, initial=0, widget=forms.NumberInput(attrs={'class': 'input-duration-small'}))
    hours = forms.IntegerField(min_value=0, max_value=23, initial=0, widget=forms.NumberInput(attrs={'class': 'input-duration-small'}))
    minutes = forms.IntegerField(min_value=0, max_value=59, initial=0, widget=forms.NumberInput(attrs={'class': 'input-duration-small'}))

    class Meta:
        model = UserSettings
        fields = ['article_duration']
        widgets = {
            'article_duration': forms.HiddenInput()
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        duration = self.instance.article_duration
        self.fields['days'].initial = duration.days
        self.fields['hours'].initial = duration.seconds // 3600
        self.fields['minutes'].initial = (duration.seconds % 3600) // 60

    def clean(self):
        cleaned_data = super().clean()
        days = cleaned_data.get('days', 0)
        hours = cleaned_data.get('hours', 0)
        minutes = cleaned_data.get('minutes', 0)
        
        cleaned_data['article_duration'] = datetime.timedelta(
            days=days,
            hours=hours,
            minutes=minutes
        )
        return cleaned_data
