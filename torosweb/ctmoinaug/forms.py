from django import forms

from .models import Activity

class ActivityForm(forms.ModelForm):
    comment = forms.CharField(widget=forms.Textarea(), required=False)
    description = forms.CharField(widget=forms.Textarea(), required=False)

    class Meta:
        model = Activity
        exclude = ('status',)
