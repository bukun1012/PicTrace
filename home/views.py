from django.shortcuts import render, redirect
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.tokens import default_token_generator
from posts.models import Post, Like


# Create your views here.
def home_view(request):
    posts = Post.objects.all().order_by("-created_at")[
        :5
    ]  # 按照時間排序，最新的貼文在最上方
    # 取得當前用戶已按愛心的貼文ID
    liked_posts = []
    if request.user.is_authenticated:
        liked_posts = Like.objects.filter(user=request.user).values_list(
            "post_id", flat=True
        )

    return render(
        request,
        "home/home.html",
        {
            "posts": posts,
            "liked_posts": liked_posts,  # 傳遞已按愛心的貼文ID清單
        },
    )


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


def home(request):
    posts = Post.objects.all().order_by("-created_at")[:5]  # 顯示最新 5 篇貼文
    return render(request, "home/home.html", {"posts": posts})
