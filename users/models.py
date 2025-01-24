from django.db import models
from django import forms


class SimpleUserCreationForm(forms.Form):
    username = forms.CharField(max_length=150, required=True)
    password1 = forms.CharField(widget=forms.PasswordInput, min_length=8, required=True)
    password2 = forms.CharField(widget=forms.PasswordInput, min_length=8, required=True)
