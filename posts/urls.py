from django.urls import path
from .views import create_post

app_name = "posts"

urlpatterns = [
    path("new/", create_post, name="create_post"),  # 設定新增貼文路由
]
