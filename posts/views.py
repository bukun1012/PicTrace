from django.http import JsonResponse, HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from .models import Post, Like, Comment
from .forms import PostForm, CommentForm
from users.utils import upload_to_s3
from django.contrib.auth.decorators import login_required
from django.contrib import messages


# 發布貼文
@login_required
def create_post(request):
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES)

        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user

            # ✅ 儲存位置欄位
            post.location = request.POST.get("location", "")

            # ✅ 確認圖片存在
            if not request.FILES.get("image"):
                messages.error(request, "圖片是必填的！")
                return redirect("home:home")

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

            messages.success(request, "貼文已成功發布！")
            return redirect("home:home")

        messages.error(request, "表單驗證失敗，請檢查輸入內容")
        return redirect("home:home")

    else:
        form = PostForm()

    return render(request, "posts/create_post.html", {"form": form})


# 編輯貼文
@login_required
@login_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    # 確保只能編輯自己的貼文
    if post.author != request.user:
        return JsonResponse({"success": False, "error": "你無權限編輯這篇貼文。"})

    if request.method == "POST":
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            edited_post = form.save(commit=False)
            edited_post.author = request.user

            # ✅ 處理圖片邏輯：保留原圖片或替換
            if request.FILES.get("image"):
                image = request.FILES["image"]

                # 檢查檔案大小 (限制 5MB)
                if image.size > 5 * 1024 * 1024:
                    return JsonResponse(
                        {"success": False, "error": "圖片大小超過 5MB 限制"}
                    )

                # 檢查檔案類型 (僅允許 JPEG 和 PNG)
                if hasattr(image, "content_type") and image.content_type not in [
                    "image/jpeg",
                    "image/png",
                ]:
                    return JsonResponse(
                        {"success": False, "error": "僅支援 JPEG 和 PNG 圖片格式"}
                    )

                # 上傳新圖片至 S3
                image.seek(0)
                file_url = upload_to_s3(image)
                if file_url:
                    edited_post.image_url = file_url  # ✅ 替換為新圖片

            elif not post.image_url:
                # ✅ 如果沒有現有圖片也沒上傳新圖片，拒絕提交
                return JsonResponse(
                    {"success": False, "error": "每篇貼文必須包含圖片。"}
                )

            # ✅ 更新其他欄位
            edited_post.content = request.POST.get("content", post.content)
            edited_post.location = request.POST.get("location", post.location)

            edited_post.save()

            return JsonResponse({"success": True, "message": "貼文已更新成功！"})

        # 表單驗證失敗
        errors = form.errors.as_json()
        return JsonResponse(
            {"success": False, "error": "表單驗證失敗", "details": errors}
        )

    return JsonResponse({"success": False, "error": "無效的請求方法。"})


# 刪除貼文
@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    # 確保只能刪除自己的貼文
    if post.author != request.user:
        return HttpResponseForbidden("你無權限刪除這篇貼文。")

    if request.method == "POST":
        post.delete()
        return redirect("home:home")  # 刪除後返回首頁

    return HttpResponseForbidden("無效的請求方法。")


# 點擊看詳細貼文並顯示留言
def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    user_has_liked = False
    if request.user.is_authenticated:
        user_has_liked = Like.objects.filter(user=request.user, post=post).exists()

    # ✅ 獲取貼文的留言
    comments = Comment.objects.filter(post=post).order_by("-created_at")

    # ✅ 留言表單
    comment_form = CommentForm()

    return render(
        request,
        "posts/post_detail.html",
        {
            "post": post,
            "user_has_liked": user_has_liked,
            "comments": comments,
            "comment_form": comment_form,
        },
    )


# 按愛心/取消愛心的 API
@login_required
def toggle_like(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    user = request.user

    # 檢查用戶是否已經按過愛心
    liked = Like.objects.filter(user=user, post=post).first()

    if liked:
        # 如果已經按過，則取消愛心
        liked.delete()
        liked_status = False
    else:
        # 尚未按過，新增一個 Like
        Like.objects.create(user=user, post=post)
        liked_status = True

    return JsonResponse(
        {
            "liked": liked_status,
            "like_count": post.likes.count(),
        }
    )


# ✅ 新增留言
@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if request.method == "POST":
        content = request.POST.get("content", "").strip()

        if content:
            # 新增留言
            Comment.objects.create(post=post, author=request.user, content=content)

            return JsonResponse(
                {
                    "success": True,
                    "comment_count": post.comments.count(),  # 確認 post.comments 設置正確
                }
            )

        # 處理空留言內容
        return JsonResponse({"success": False, "error": "留言內容不能為空"})

    return HttpResponseForbidden("不允許的請求方法")
