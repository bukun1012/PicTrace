from django import forms
from .models import Profile
import re
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["avatar"]


class SimpleUserCreationForm(forms.Form):
    username = forms.CharField(max_length=150, required=True)
    email = forms.EmailField(
        required=True,
    )
    password1 = forms.CharField(widget=forms.PasswordInput, required=True)
    password2 = forms.CharField(widget=forms.PasswordInput, required=True)

    def clean_username(self):
        username = self.cleaned_data.get("username")
        if User.objects.filter(username=username).exists():
            raise ValidationError("該用戶名已被使用，請選擇其他用戶名。")
        return username

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if not email:
            return email  # 讓 Django 內建的 EmailField 自動處理格式錯誤

        # 只有當 email 存在且格式正確時才執行查詢
        if email and User.objects.filter(email=email).exists():
            raise ValidationError("該電子郵件已被註冊")

        return email

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        # 確保兩次密碼輸入一致
        if password1 and password2 and password1 != password2:
            self.add_error("password2", "兩次密碼不一致")

        # 分開檢查密碼長度和是否包含英文字母+數字
        if password1:
            if len(password1) < 8:
                self.add_error("password1", "密碼必須至少 8 個字元")
            elif not re.search(r"[A-Za-z]", password1) or not re.search(
                r"\d", password1
            ):
                self.add_error("password1", "密碼必須包含英文字母與數字")

        return cleaned_data
