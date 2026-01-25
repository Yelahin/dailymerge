from django import forms
from feeds.models import Source

class SourceForm(forms.ModelForm):
    class Meta:
        model = Source 
        fields = ['url', 'category', 'active', 'params', 'source_type']

    def __init__(self, *args, **kwargs):
        user_settings = kwargs.pop('user_settings', None)
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = user_settings.categories.all()