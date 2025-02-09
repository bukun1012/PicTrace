from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.utils.text import slugify
from django.contrib.auth import get_user_model
from allauth.socialaccount.models import SocialAccount
from django.contrib.auth.hashers import make_password
from django.shortcuts import redirect

User = get_user_model()


class MySocialAccountAdapter(DefaultSocialAccountAdapter):
    def is_auto_signup_allowed(self, request, sociallogin):
        """允許所有第三方登入的用戶自動註冊，而不跳到額外的表單"""
        return True  # 直接允許 auto signup

    def get_login_redirect_url(self, request):
        """確保第三方登入後能直接回首頁"""
        return "/"

    def populate_user(self, request, sociallogin, data):
        """確保 Google / LINE 登入時有 username"""
        user = super().populate_user(request, sociallogin, data)

        if not user.username:
            provider = sociallogin.account.provider  # google / line
            email = user.email or sociallogin.account.extra_data.get("email", "")
            uid = sociallogin.account.uid  # LINE / Google UID

            if provider == "google" and email:
                user.username = slugify(email.split("@")[0])
            elif provider == "line":
                user.username = f"line_{uid}"
            else:
                user.username = f"user_{uid}"  # 其他未知 provider

            # 確保 username 唯一
            original_username = user.username
            counter = 1
            while User.objects.filter(username=user.username).exists():
                user.username = f"{original_username}_{counter}"
                counter += 1

        return user

    def pre_social_login(self, request, sociallogin):
        """自動關聯帳號並處理 LINE 直接註冊"""
        provider = sociallogin.account.provider  # google / line
        user_email = sociallogin.account.extra_data.get("email", "")
        user_uid = sociallogin.account.uid

        # **Google 登入邏輯**
        if provider == "google" and user_email:
            try:
                existing_user = User.objects.get(email=user_email)
                if not SocialAccount.objects.filter(
                    user=existing_user, provider="google"
                ).exists():
                    sociallogin.connect(request, existing_user)  # 綁定 Google
                return  # 直接登入
            except User.DoesNotExist:
                pass  # 讓 allauth 自行處理

        # **LINE 登入邏輯**
        if provider == "line":
            # Step 1: 檢查該 LINE UID 是否已存在
            try:
                existing_social_account = SocialAccount.objects.get(
                    provider="line", uid=user_uid
                )
                sociallogin.connect(request, existing_social_account.user)
                return  # 直接登入
            except SocialAccount.DoesNotExist:
                pass  # 沒找到 LINE 記錄，繼續處理

            # Step 2: 檢查 email 是否已存在，若存在則綁定
            if user_email:
                try:
                    existing_user = User.objects.get(email=user_email)
                    if not SocialAccount.objects.filter(
                        user=existing_user, provider="line"
                    ).exists():
                        sociallogin.connect(request, existing_user)
                    return  # 直接登入
                except User.DoesNotExist:
                    pass  # 沒有找到 email，繼續創建帳號

            # Step 3: **自動創建新帳戶**
            new_user = User.objects.create_user(
                username=f"line_{user_uid}",
                email=user_email if user_email else "",
                password=make_password(None),
            )
            sociallogin.connect(request, new_user)
            sociallogin.state["process"] = "connect"  # 直接登入
