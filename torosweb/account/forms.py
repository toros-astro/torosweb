from django.contrib.auth.forms import UserCreationForm
from django import forms
from .models import User

class RegistrationForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    # email = forms.EmailField(max_length=75, required=True)

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email", "affiliation")

    def save(self, commit=True):
        user = super(RegistrationForm, self).save(commit=False)
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        user.email = self.cleaned_data["email"]
        user.affiliation = self.cleaned_data["affiliation"]
        if commit:
            user.save()
        return user