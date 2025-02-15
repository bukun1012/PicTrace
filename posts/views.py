from django.shortcuts import render, redirect
from .models import Post
from .forms import PostForm
from users.utils import upload_to_s3
from django.contrib.auth.decorators import login_required


@login_required
def create_post(request):
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES)

        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user

            # ✅ 如果有上傳圖片，則上傳至 S3，並存儲 URL
            if request.FILES.get("image"):
                image = request.FILES["image"]

                # 檢查檔案大小 (限制 5MB)
                if image.size > 5 * 1024 * 1024:
                    return redirect("posts:create_post")

                # 檢查檔案類型 (僅允許 JPEG 和 PNG)
                if hasattr(image, "content_type") and image.content_type not in [
                    "image/jpeg",
                    "image/png",
                ]:
                    return redirect("posts:create_post")

                # ✅ 使用 `upload_to_s3` 上傳圖片
                image.seek(0)
                file_url = upload_to_s3(image)
                if file_url:
                    post.image_url = file_url

            post.save()  # ✅ 儲存貼文
            return redirect("home:home")

    else:
        form = PostForm()

    return render(request, "posts/create_post.html", {"form": form})
