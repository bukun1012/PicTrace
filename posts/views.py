from django.http import JsonResponse
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
                    return JsonResponse({"error": "圖片大小超過 5MB 限制"}, status=400)

                # 檢查檔案類型 (僅允許 JPEG 和 PNG)
                if hasattr(image, "content_type") and image.content_type not in [
                    "image/jpeg",
                    "image/png",
                ]:
                    return JsonResponse(
                        {"error": "僅支援 JPEG 和 PNG 圖片格式"}, status=400
                    )

                # ✅ 使用 `upload_to_s3` 上傳圖片
                image.seek(0)
                file_url = upload_to_s3(image)
                if file_url:
                    post.image_url = file_url

            post.save()  # ✅ 儲存貼文

            # ✅ 回應 JSON 給前端
            return JsonResponse(
                {
                    "message": "貼文發佈成功",
                    "post_id": post.id,
                    "image_url": post.image_url,
                },
                status=200,
            )

        return JsonResponse({"error": "表單驗證失敗"}, status=400)

    else:
        form = PostForm()

    return render(request, "posts/create_post.html", {"form": form})
