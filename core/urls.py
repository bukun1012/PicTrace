from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("home.urls")),  # 將空路徑指向 users 應用
    path("users/", include("users.urls")),  # 將空路徑指向 users 應用
    path("accounts/", include("allauth.urls")),  # allauth 的路由
]
