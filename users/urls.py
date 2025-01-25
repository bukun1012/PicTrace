from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings

app_name = "users"

urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("register/", views.register_view, name="register"),
    path("logout/", views.logout_view, name="logout"),
    path("", views.home_view, name="home"),
    path("upload_avatar/", views.upload_avatar, name="upload_avatar"),
    path("profile/", views.profile_view, name="profile"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
