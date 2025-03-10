from pathlib import Path
import os
from dotenv import load_dotenv

# 加載環境變數
load_dotenv()

# ==========================
# 路徑配置
# ==========================
BASE_DIR = Path(__file__).resolve().parent.parent

# ==========================
# 安全性配置
# ==========================
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "your-default-secret-key")

DEBUG = os.getenv("DEBUG", "True") == "True"

ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

PROTOCOL = os.getenv("PROTOCOL", "http")

DEFAULT_DOMAIN = os.getenv("DEFAULT_DOMAIN", "127.0.0.1:8000")

# ==========================
# 已安裝的 APP
# ==========================
INSTALLED_APPS = [
    # Django 預設應用
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",  # allauth 需要這個
    # 自定義 APP
    "home",
    "users",
    "storages",
    "posts",
    # 第三方 APP
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.google",
    "allauth.socialaccount.providers.line",
]

# ==========================
# Middleware 中間件
# ==========================
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "allauth.account.middleware.AccountMiddleware",
]

# ==========================
# URL 配置
# ==========================
ROOT_URLCONF = "core.urls"

# ==========================
# 模板配置
# ==========================
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "core.wsgi.application"

# ==========================
# 數據庫配置
# ==========================
DATABASES = {
    "default": {
        "ENGINE": os.getenv("DB_ENGINE", "django.db.backends.sqlite3"),
        "NAME": os.getenv("DB_NAME", BASE_DIR / "db.sqlite3"),
        "USER": os.getenv("DB_USER", ""),
        "PASSWORD": os.getenv("DB_PASSWORD", ""),
        "HOST": os.getenv("DB_HOST", "localhost"),
        "PORT": os.getenv("DB_PORT", ""),
    }
}

# ==========================
# 密碼驗證
# ==========================
# AUTH_PASSWORD_VALIDATORS = [
# {
# "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
# },
# {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
# {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
# {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
# ]

# ==========================
# 語言 & 時區
# ==========================
LANGUAGE_CODE = "zh-hant"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# ==========================
# 靜態文件
# ==========================
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]

# ==========================
# 預設主鍵字段
# ==========================
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# AWS S3 配置
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_STORAGE_BUCKET_NAME = os.getenv("AWS_STORAGE_BUCKET_NAME")
AWS_S3_REGION_NAME = os.getenv("AWS_S3_REGION_NAME")

AWS_S3_CUSTOM_DOMAIN = f"{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com"

# 使用 S3 儲存上傳的文件
DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
MEDIA_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/"
# MEDIA_ROOT = BASE_DIR / "media"
# ==========================
# 郵件服務 (Gmail)
# ==========================
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")
DEFAULT_FROM_EMAIL = f"PicTrace <{EMAIL_HOST_USER}>"

# ==========================
# 站點 & 認證
# ==========================
SITE_ID = 1
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]

# ==========================
# Django-AllAuth 設定
# ==========================
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"
ACCOUNT_AUTHENTICATION_METHOD = "username_email"
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = "none"
SOCIALACCOUNT_AUTO_SIGNUP = True
ACCOUNT_SIGNUP_REDIRECT_URL = "/"
SOCIALACCOUNT_EMAIL_REQUIRED = True
SOCIALACCOUNT_EMAIL_VERIFICATION = "none"
SOCIALACCOUNT_ADAPTER = "users.adapters.MySocialAccountAdapter"
SOCIALACCOUNT_LOGIN_ON_GET = True  # 直接跳過 Google 登入確認頁面

# ==========================
# Google OAuth2 設定
# ==========================
SOCIALACCOUNT_PROVIDERS = {
    "google": {
        "SCOPE": ["profile", "email"],
        "AUTH_PARAMS": {"access_type": "online"},
    },
    "line": {
        "SCOPE": ["openid", "profile", "email"],  # 啟用 Email 權限
        "AUTH_PARAMS": {"prompt": "consent"},  # 讓用戶每次登入都同意授權
    },
}

# ==========================
# 訊息管理
# ==========================
MESSAGE_STORAGE = "django.contrib.messages.storage.session.SessionStorage"


SOCIALACCOUNT_PROVIDERS["line"]["APP"] = {
    "client_id": "2006880194",
    "secret": "4141cf5f4ffe99e96406f54072270b09",
}

SOCIALACCOUNT_SIGNUP_REDIRECT_URL = "/"  # 註冊後直接回到首頁
SOCIALACCOUNT_LOGIN_REDIRECT_URL = "/"  # 第三方登入後直接回到首頁
