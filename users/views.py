from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django import forms


# 登入
def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("users:home")  # 登入後跳轉到首頁
    else:
        form = AuthenticationForm()
    return render(request, "users/login.html", {"form": form})


# 註冊
# 用戶註冊表單（只包含用戶名和密碼）
class SimpleUserCreationForm(forms.Form):
    username = forms.CharField(max_length=150, required=True)
    password1 = forms.CharField(widget=forms.PasswordInput, min_length=8, required=True)
    password2 = forms.CharField(widget=forms.PasswordInput, min_length=8, required=True)

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 != password2:
            raise forms.ValidationError("兩次密碼不一致")
        return cleaned_data


# 註冊視圖
def register_view(request):
    if request.method == "POST":
        form = SimpleUserCreationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password1"]
            user = User.objects.create_user(username=username, password=password)
            login(request, user)
            return redirect("users:login")
    else:
        form = SimpleUserCreationForm()

    return render(request, "users/register.html", {"form": form})


# 登出
def logout_view(request):
    if request.method == "POST":
        logout(request)
        return redirect("users:home")


def home_view(request):
    return render(request, "users/home.html")
