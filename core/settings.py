from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()  # 讀取 .env 文件的套件

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-w3a%dsaeh8fzo6fv@-n6az(=ggl-f8qhxlz4wgd6=7x3t*n0gz"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["localhost", "127.0.0.1"]


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "users",
    "django.contrib.sites",  # 必須加入，否則 allauth 會報錯
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.google",  # 加入 Google 第三方登入
]

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

ROOT_URLCONF = "core.urls"

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


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": os.getenv("DB_ENGINE"),
        "NAME": os.getenv("DB_NAME"),
        "USER": os.getenv("DB_USER"),
        "PASSWORD": os.getenv("DB_PASSWORD"),
        "HOST": os.getenv("DB_HOST"),
        "PORT": os.getenv("DB_PORT"),
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = "zh-hant"  # 預設成中文

TIME_ZONE = "UTC"

USE_I18N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]


# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Gmail 配置 (使用 Google 作為郵件服務提供者)
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False
EMAIL_HOST_USER = "dalonbukun@gmail.com"  # 你的 Gmail 帳號
EMAIL_HOST_PASSWORD = "oluccspeisrwgqgc"  # PicTrace應用程式密碼
DEFAULT_FROM_EMAIL = "PicTrace <dalonbukun@gmail.com>"  # 預設發件人

# 指定基礎域名
# 替換 `DEFAULT_DOMAIN` 和 `PROTOCOL` 為您的開發環境
DEFAULT_DOMAIN = os.getenv("DEFAULT_DOMAIN", "localhost:8000")
PROTOCOL = os.getenv("PROTOCOL", "http")

# google site id
SITE_ID = 1

# google身份驗證後備端
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]

# allauth 登入相關 URL
LOGIN_REDIRECT_URL = "/"  # 登入後的重導向頁面
LOGOUT_REDIRECT_URL = "/"  # 登出後的重導向頁面
ACCOUNT_AUTHENTICATION_METHOD = "username_email"
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = "none"
SOCIALACCOUNT_AUTO_SIGNUP = True  # 允許自動註冊
ACCOUNT_SIGNUP_REDIRECT_URL = "/"  # 註冊後的重導向頁面（可設定為首頁）
SOCIALACCOUNT_EMAIL_REQUIRED = True  # 確保 Google 提供 email
SOCIALACCOUNT_EMAIL_VERIFICATION = "none"  # 設定 email 驗證為 "none"，避免多一步驗證
SOCIALACCOUNT_ADAPTER = "users.adapters.MySocialAccountAdapter"  # 自動產生使用者名稱
SOCIALACCOUNT_LOGIN_ON_GET = True  # 直接跳過 Google 登入確認頁面

# Google OAuth2 設定
SOCIALACCOUNT_PROVIDERS = {
    "google": {
        "SCOPE": ["profile", "email"],
        "AUTH_PARAMS": {"access_type": "online"},
    }
}

MESSAGE_STORAGE = "django.contrib.messages.storage.session.SessionStorage"
