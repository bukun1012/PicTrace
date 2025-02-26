from django.urls import path
from .views import (
    create_post,
    edit_post,
    delete_post,
    post_detail,
    toggle_like,
    add_comment,
    edit_comment,
    delete_comment,
)

app_name = "posts"

urlpatterns = [
    path("new/", create_post, name="create_post"),  # 新增貼文
    path("<int:post_id>/", post_detail, name="post_detail"),
    path("<int:post_id>/edit/", edit_post, name="edit_post"),  # 編輯貼文
    path("<int:post_id>/delete/", delete_post, name="delete_post"),  # 刪除貼文
    path("like/<int:post_id>/", toggle_like, name="toggle_like"),  # 按愛心功能
    path("<int:post_id>/comment/", add_comment, name="add_comment"),  # 新增留言功能
    path(
        "comments/<int:comment_id>/edit/", edit_comment, name="edit_comment"
    ),  # 編輯留言功能
    path(
        "comments/<int:comment_id>/delete/", delete_comment, name="delete_comment"
    ),  # 刪除留言功能
]
