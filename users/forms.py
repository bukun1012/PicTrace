from django import forms
from .models import Profile
from django.contrib.auth.forms import SetPasswordForm
import re


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["avatar"]


class CustomSetPasswordForm(SetPasswordForm):
    """自訂密碼重設表單，確保錯誤訊息與註冊一致"""

    def clean_new_password1(self):
        """驗證新密碼"""
        password1 = self.cleaned_data.get("new_password1")

        errors = []

        # ✅ 檢查密碼長度
        if len(password1) < 8:
            errors.append("密碼必須至少 8 個字元")

        # ✅ 檢查密碼是否包含英文字母與數字
        if not re.search(r"[A-Za-z]", password1) or not re.search(r"\d", password1):
            errors.append("密碼必須包含英文字母與數字")

        if errors:
            raise forms.ValidationError(errors)

        return password1

    def clean(self):
        """檢查密碼是否一致"""
        cleaned_data = super().clean()
        password1 = cleaned_data.get("new_password1")
        password2 = cleaned_data.get("new_password2")

        if password1 and password2 and password1 != password2:
            self.add_error("new_password2", "兩次密碼不一致")

        return cleaned_data
