from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings

app_name = "users"

urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("register/", views.register_view, name="register"),
    path("logout/", views.logout_view, name="logout"),
    path("upload_avatar/", views.upload_avatar, name="upload_avatar"),
    path("profile/", views.profile_view, name="profile"),
    path(
        "password_reset/",
        views.CustomPasswordResetView.as_view(),
        name="password_reset",
    ),
    path(
        "password_reset/done/",
        views.CustomPasswordResetDoneView.as_view(),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        views.CustomPasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path(
        "reset_done/",
        views.CustomPasswordResetCompleteView.as_view(),
        name="password_reset_complete",
    ),
    path("check-email/", views.check_email_view, name="check_email"),
    path(
        "resend-verification/",
        views.resend_verification_email_view,
        name="resend_verification",
    ),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
