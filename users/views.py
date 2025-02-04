from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from .models import Profile
from django.contrib.auth.decorators import login_required
from .forms import ProfileForm
from django.contrib import messages
from .utils import upload_to_s3
from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView
from django.urls import reverse_lazy
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth import authenticate
from .forms import SimpleUserCreationForm

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
            return redirect("home:home")
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

            # 轉向檢查信箱頁面，並帶上 email 參數
            return redirect(f"{reverse_lazy('users:check_email')}?email={email}")

    else:
        form = SimpleUserCreationForm()

    return render(request, "users/register.html", {"form": form})


# 檢查電子郵件的頁面
def check_email_view(request):
    email = request.GET.get("email")  # 取得用戶註冊時的 email
    return render(request, "users/check_email.html", {"email": email})


# 處理重新發送驗證郵件的請求
def resend_verification_email_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        user = get_object_or_404(User, email=email)

        if not user.is_active:
            # 產生新的驗證連結
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            domain = settings.DEFAULT_DOMAIN
            protocol = settings.PROTOCOL
            activation_link = f"{protocol}://{domain}/activate/{uid}/{token}/"

            # 發送驗證信
            subject = "PicTrace 註冊驗證 (重新發送)"
            message = render_to_string(
                "users/activation_email.html",
                {
                    "username": user.username,
                    "activation_link": activation_link,
                },
            )

            email_msg = EmailMessage(
                subject, message, settings.DEFAULT_FROM_EMAIL, [email]
            )
            email_msg.content_subtype = "html"
            email_msg.send()

            messages.success(request, "驗證郵件已重新發送！請檢查您的信箱。")
        else:
            messages.info(request, "您的帳號已經驗證過，請直接登入。")

    return redirect(f"{reverse_lazy('users:check_email')}?email={email}")


# 登出
def logout_view(request):
    if request.method == "POST":
        logout(request)
        return redirect("home:home")


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
