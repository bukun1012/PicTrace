from django import forms
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User


class SimpleUserCreationForm(forms.Form):
    username = forms.CharField(max_length=150, required=True)
    email = forms.EmailField(required=True, validators=[validate_email])
    password1 = forms.CharField(widget=forms.PasswordInput, min_length=8, required=True)
    password2 = forms.CharField(widget=forms.PasswordInput, min_length=8, required=True)

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise ValidationError("該電子郵件已被註冊")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 != password2:
            raise forms.ValidationError("兩次密碼不一致")
        return cleaned_data
