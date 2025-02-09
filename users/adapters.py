from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.utils.text import slugify
from django.contrib.auth import get_user_model
from allauth.socialaccount.models import SocialAccount

User = get_user_model()


class MySocialAccountAdapter(DefaultSocialAccountAdapter):
    def populate_user(self, request, sociallogin, data):
        """確保 Google 登入時有 username，如果沒有則使用 email 來產生"""
        user = super().populate_user(request, sociallogin, data)
        if not user.username:
            user.username = slugify(user.email.split("@")[0])  # 用 email 當 username
            while User.objects.filter(username=user.username).exists():
                user.username += str(User.objects.count())  # 避免 username 重複
        return user

    def pre_social_login(self, request, sociallogin):
        """自動關聯 Google 帳戶與現有 email 帳戶"""
        user_email = sociallogin.account.extra_data.get("email")

        if not user_email:
            return  # 如果沒有 email，直接返回，讓 allauth 處理

        try:
            existing_user = User.objects.get(email=user_email)

            # 確保這個 email 還沒綁定任何社交帳號
            if not SocialAccount.objects.filter(user=existing_user).exists():
                sociallogin.connect(request, existing_user)
            else:
                # 如果 email 已經綁定了一個 Google 帳戶，則讓 Allauth 處理
                pass

        except User.DoesNotExist:
            pass  # 如果 email 沒有被註冊過，讓 allauth 正常創建新帳戶
