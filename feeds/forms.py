from django import forms
from feeds.models import Source

class SourceForm(forms.ModelForm):
    class Meta:
        model = Source 
        fields = ['url', 'source_type']