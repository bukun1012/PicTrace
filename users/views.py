from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django import forms
from .models import SimpleUserCreationForm
from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView
from django.urls import reverse_lazy
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.contrib import messages


# 登入
def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("users:home")  # 登入後跳轉到首頁
        else:
            # 如果表單無效，顯示錯誤訊息
            messages.error(request, "帳戶名或密碼錯誤")
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
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password1"]

            # 創建用戶並保存到資料庫
            User.objects.create_user(username=username, email=email, password=password)

            # 添加成功提示訊息
            messages.success(request, f"註冊成功！歡迎您，{username}！")

            # 跳轉到登入頁面
            return redirect("users:login")
    else:
        form = SimpleUserCreationForm()

    # 渲染註冊頁面
    return render(request, "users/register.html", {"form": form})


# 登出
def logout_view(request):
    if request.method == "POST":
        logout(request)
        return redirect("users:home")


def home_view(request):
    return render(request, "users/home.html")


# 忘記密碼相關
# 自定義的 PasswordResetView
class CustomPasswordResetView(PasswordResetView):
    template_name = "users/password_reset.html"
    email_template_name = "users/password_reset_email.html"  # 使用html模板
    subject_template_name = "users/password_reset_subject.txt"  # 自定義郵件標題模板
    success_url = reverse_lazy("users:password_reset_done")
    extra_context = {
        "protocol": settings.PROTOCOL,
        "domain": settings.DEFAULT_DOMAIN,
    }

    def form_valid(self, form):
        """覆蓋郵件發送邏輯，避免重複發送"""
        email = form.cleaned_data["email"]

        for user in form.get_users(email):
            context = {
                "email": email,
                "domain": settings.DEFAULT_DOMAIN,
                "protocol": settings.PROTOCOL,
                "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                "token": default_token_generator.make_token(user),
            }
            subject = render_to_string(self.subject_template_name, context).strip()
            html_message = render_to_string(self.email_template_name, context)

            # 發送郵件
            email_msg = EmailMessage(
                subject=subject,
                body=html_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[email],
            )
            email_msg.content_subtype = "html"  # 設置內容類型為 HTML
            email_msg.send()

        # 不再調用的郵件發送邏輯
        return super(auth_views.PasswordResetView, self).form_valid(form)


# 自定義的 PasswordResetDoneView
class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = "users/password_reset_done.html"  # 自定義模板的路徑


# 自定義的 PasswordResetConfirmView
class CustomPasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    template_name = "users/password_reset_confirm.html"
    success_url = reverse_lazy("users:password_reset_complete")


# 自定義的 PasswordResetCompleteView
class CustomPasswordResetCompleteView(auth_views.PasswordResetCompleteView):
    template_name = "users/password_reset_complete.html"
