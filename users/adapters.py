from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.utils.text import slugify
from django.contrib.auth.models import User


class MySocialAccountAdapter(DefaultSocialAccountAdapter):
    def populate_user(self, request, sociallogin, data):
        user = super().populate_user(request, sociallogin, data)
        if not user.username:
            user.username = slugify(user.email.split("@")[0])  # 用 email 當 username
            while User.objects.filter(username=user.username).exists():
                user.username += str(User.objects.count())  # 避免 username 重複
        return user
