from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django import forms
from .models import SimpleUserCreationForm, Profile
from django.contrib.auth.decorators import login_required
from .forms import ProfileForm
from django.contrib import messages
from .utils import upload_to_s3


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


@login_required
def upload_avatar(request):
    if request.method == "POST" and request.FILES.get("avatar"):
        avatar = request.FILES["avatar"]

        # 檢查檔案大小 (限制 5 MB)
        if avatar.size > 5 * 1024 * 1024:
            messages.error(request, "The file size exceeds the 5MB limit.")
            return redirect("users:upload_avatar")

        # 檢查檔案類型 (僅允許 JPEG 和 PNG)
        if not hasattr(avatar, "content_type") or avatar.content_type not in [
            "image/jpeg",
            "image/png",
        ]:
            messages.error(request, "Only JPEG and PNG files are allowed.")
            return redirect("users:upload_avatar")

        # 上傳檔案到 S3
        file_url = upload_to_s3(avatar)

        if file_url:
            # 更新或創建用戶資料
            user_profile, created = Profile.objects.get_or_create(user=request.user)
            user_profile.avatar = file_url
            user_profile.save()

            messages.success(request, "Avatar uploaded successfully!")
        else:
            messages.error(request, "Failed to upload avatar. Please try again.")

        return redirect("users:profile")

    return render(request, "users/upload_avatar.html", {"form": ProfileForm()})


@login_required
def profile_view(request):
    # 獲取用戶的 Profile 資訊，顯示頭像 URL
    user_profile = Profile.objects.filter(user=request.user).first()
    avatar_url = user_profile.avatar if user_profile and user_profile.avatar else None

    return render(request, "users/profile.html", {"avatar_url": avatar_url})
