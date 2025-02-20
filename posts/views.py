from django.http import JsonResponse, HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from .models import Post
from .forms import PostForm
from users.utils import upload_to_s3
from django.contrib.auth.decorators import login_required
from django.contrib import messages


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


# ✅ 編輯貼文
@login_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    # 確保只能編輯自己的貼文
    if post.author != request.user:
        return HttpResponseForbidden("你無權限編輯這篇貼文。")

    if request.method == "POST":
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            edited_post = form.save(commit=False)
            edited_post.author = request.user

            # ✅ 如果有新圖片，則上傳至 S3
            if request.FILES.get("image"):
                image = request.FILES["image"]

                # 檢查檔案大小 (限制 5MB)
                if image.size > 5 * 1024 * 1024:
                    messages.error(request, "圖片大小超過 5MB 限制")
                    return redirect("home:home")

                # 檢查檔案類型 (僅允許 JPEG 和 PNG)
                if hasattr(image, "content_type") and image.content_type not in [
                    "image/jpeg",
                    "image/png",
                ]:
                    messages.error(request, "僅支援 JPEG 和 PNG 圖片格式")
                    return redirect("home:home")

                # 上傳新圖片至 S3
                image.seek(0)
                file_url = upload_to_s3(image)
                if file_url:
                    edited_post.image_url = file_url

            edited_post.save()

            # ✅ 加入成功訊息並跳轉回首頁
            messages.success(request, "貼文已更新成功！")
            return redirect("home:home")

        # 如果表單驗證失敗
        messages.error(request, "表單驗證失敗，請檢查輸入內容")
        return redirect("home:home")

    else:
        form = PostForm(instance=post)

    return render(request, "posts/edit_post.html", {"form": form, "post": post})


# ✅ 刪除貼文
@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    # 確保只能刪除自己的貼文
    if post.author != request.user:
        return HttpResponseForbidden("你無權限刪除這篇貼文。")

    if request.method == "POST":
        post.delete()
        messages.success(request, "貼文已成功刪除！")  # ✅ 新增成功訊息
        return redirect("home:home")  # ✅ 刪除後返回首頁

    return render(request, "posts/confirm_delete.html", {"post": post})
