from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path("admin/", admin.site.urls),
    path("users/", include("users.urls")),  # 包含 users 應用的路由
    path("", include("users.urls")),  # 將空路徑指向 users 應用
]
