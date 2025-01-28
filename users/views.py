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
from django.contrib.auth import authenticate

# from django.shortcuts import get_object_or_404 尚未使用404頁面


# 登入
def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        username = request.POST.get("username")
        password = request.POST.get("password")

        # 使用 `authenticate` 檢查用戶名和密碼
        user = authenticate(request, username=username, password=password)

        if user is not None:
            # 檢查用戶是否被禁用
            if not user.is_active:
                messages.error(request, "您的帳號尚未驗證，請檢查信箱完成驗證。")
                return render(request, "users/login.html", {"form": form})

            # 如果用戶已激活，執行登入
            login(request, user)
            return redirect("users:home")
        else:
            # 檢查是否有用戶存在
            try:
                # 嘗試查詢是否有此用戶
                user = User.objects.get(username=username)
                if not user.is_active:
                    messages.error(request, "您的帳號尚未驗證，請檢查信箱完成驗證。")
                else:
                    messages.error(request, "帳戶名或密碼錯誤")
            except User.DoesNotExist:
                # 用戶不存在
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

            # 創建用戶但設為未激活
            user = User.objects.create_user(
                username=username, email=email, password=password
            )
            user.is_active = False  # 註冊時設為未激活
            user.save()

            # 發送驗證信
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            domain = settings.DEFAULT_DOMAIN
            protocol = settings.PROTOCOL
            activation_link = f"{protocol}://{domain}/activate/{uid}/{token}/"

            subject = "PicTrace 註冊驗證"
            message = render_to_string(
                "users/activation_email.html",
                {
                    "username": username,
                    "activation_link": activation_link,
                },
            )

            email_msg = EmailMessage(
                subject, message, settings.DEFAULT_FROM_EMAIL, [email]
            )
            email_msg.content_subtype = "html"  # 設置為 HTML 格式
            email_msg.send()

            messages.success(request, "註冊成功！請檢查您的信箱，完成帳號驗證。")
            return redirect("users:login")
    else:
        form = SimpleUserCreationForm()

    return render(request, "users/register.html", {"form": form})


# 帳號激活驗證
def activate_account(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, "帳號驗證成功！現在可以登入了。")
        return redirect("users:login")
    else:
        messages.error(request, "驗證連結無效或已過期。")
        return redirect("users:register")


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
