from django.shortcuts import render, redirect
from .models import Post
from .forms import PostForm
from django.contrib.auth.decorators import login_required


@login_required
def create_post(request):
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user  # 設定貼文的作者
            post.save()
            return redirect("home:home")  # 發布成功後跳轉回首頁
    else:
        form = PostForm()

    return render(request, "posts/create_post.html", {"form": form})
