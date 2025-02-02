from django.urls import path
from . import views

app_name = "home"

urlpatterns = [
    path("", views.home_view, name="home"),
    path("activate/<uidb64>/<token>/", views.activate_account, name="activate"),
]
