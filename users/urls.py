from django.urls import path
from . import views

app_name = "users"
urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("register/", views.register_view, name="register"),
    path("logout/", views.logout_view, name="logout"),
    path("", views.home_view, name="home"),  # 將空路徑指向 home 視圖
]
