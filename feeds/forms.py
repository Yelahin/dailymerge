from django import forms
from feeds.models import Source
from users.models import UserSource

class SourceForm(forms.ModelForm):
    url = forms.URLField(max_length=500)
    source_type = forms.ChoiceField(choices=Source.SourceType.choices)

    class Meta:
        model = UserSource
        fields = ['category', 'params', 'active']

    def __init__(self, *args, **kwargs):
        self.usersettings = kwargs.pop('usersettings', None)
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = self.usersettings.categories.all()

    def save(self, commit=True):
        usersource = super().save(commit=False)

        # For update method, save old source
        old_source = None
        if usersource.pk:
            old_source = UserSource.objects.get(pk=usersource.pk).source
        
        # Get or create Source object
        source, created = Source.objects.get_or_create(
            url=self.cleaned_data['url'],
            source_type=self.cleaned_data['source_type'],
        )
        # Set Source object for UserSource object
        usersource.source = source

        # If create object operation
        if not usersource.pk:
            usersource.usersettings = self.usersettings
        
        if commit:
            usersource.save()

            # Check if method == update and source was changed
            if old_source and old_source != source:
                # Delete source if nobody use it
                if not UserSource.objects.filter(source=old_source).exists():
                    old_source.delete()
        
        return usersource
    