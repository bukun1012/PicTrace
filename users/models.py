import re
from django import forms
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.db import models


class SimpleUserCreationForm(forms.Form):
    username = forms.CharField(max_length=150, required=True)
    email = forms.EmailField(required=True, validators=[validate_email])
    password1 = forms.CharField(widget=forms.PasswordInput, min_length=8, required=True)
    password2 = forms.CharField(widget=forms.PasswordInput, min_length=8, required=True)

    def clean_username(self):
        username = self.cleaned_data.get("username")
        if User.objects.filter(username=username).exists():
            raise ValidationError("該用戶名已被使用，請選擇其他用戶名。")
        return username

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise ValidationError("該電子郵件已被註冊")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        # 確保兩次密碼輸入一致
        if password1 and password2 and password1 != password2:
            self.add_error("password2", "兩次密碼不一致")

        # 密碼強度檢查：至少 8 個字元，包含至少一個英文字母與一個數字
        if password1 and not re.match(
            r"^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$", password1
        ):
            self.add_error(
                "password1", "密碼必須至少 8 個字元，且包含至少一個英文字母與一個數字。"
            )

        return cleaned_data


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to="avatars/", null=True, blank=True)

    def __str__(self):
        return self.user.username
