from django.urls import path
from .views import create_post, edit_post, delete_post, post_detail, toggle_like

app_name = "posts"

urlpatterns = [
    path("new/", create_post, name="create_post"),  # 新增貼文
    path("<int:post_id>/", post_detail, name="post_detail"),
    path("<int:post_id>/edit/", edit_post, name="edit_post"),  # 編輯貼文
    path("<int:post_id>/delete/", delete_post, name="delete_post"),  # 刪除貼文
    path("like/<int:post_id>/", toggle_like, name="toggle_like"),  # 按愛心功能
]
