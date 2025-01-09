import os
from datetime import timedelta
from pathlib import Path

from .env import ENV

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = "django-insecure-x$ko)6dh*=-f0k*q-49=)w$8hy3qlk4umi1zbd4ah6=7vdft=*"

DEBUG = True if ENV.DJANGO_ENV == "development" else False

ALLOWED_HOSTS = ["*"]

APPEND_SLASH = False

CORS_ALLOW_ALL_ORIGINS = True

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "drf_spectacular",
    "oauth2_provider",
    "rest_framework",
    "rest_framework_simplejwt",
    "django_filters",
    "corsheaders",
    "backend.apps.application",
    "backend.apps.authentication",
    "backend.apps.chat",
    "adrf",
    "django_apscheduler",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "djangorestframework_camel_case.middleware.CamelCaseMiddleWare",
]

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": f"redis://{ENV.REDIS_HOST}:{ENV.REDIS_PORT}/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
    }
}

ROOT_URLCONF = "backend.urls"

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

# WSGI_APPLICATION = "backend.wsgi.application"
ASGI_APPLICATION = "backend.asgi.application"

# Configure custom user model
AUTH_USER_MODEL = "authentication.User"

# Database
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": ENV.DATABASE_NAME,
        "USER": ENV.DATABASE_USER,
        "PASSWORD": ENV.DATABASE_PASSWORD,
        "HOST": ENV.DATABASE_HOST,
        "PORT": ENV.DATABASE_PORT,
    }
}

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

REST_FRAMEWORK = {
    # Global default permission configuration
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
    # Global default response configuration
    "DEFAULT_RENDERER_CLASSES": (
        "backend.utils.renderers.UnifiedResponseJsonRender",
        "djangorestframework_camel_case.render.CamelCaseJSONRenderer",
        "djangorestframework_camel_case.render.CamelCaseBrowsableAPIRenderer",
        "rest_framework.renderers.BrowsableAPIRenderer",
    ),
    # Global default parser configuration
    "DEFAULT_PARSER_CLASSES": (
        "djangorestframework_camel_case.parser.CamelCaseMultiPartParser",
        "djangorestframework_camel_case.parser.CamelCaseFormParser",
        "djangorestframework_camel_case.parser.CamelCaseJSONParser",
    ),
    # API documentation
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    # Global default authentication configuration
    "DEFAULT_AUTHENTICATION_CLASSES": (
        # OAuth2.0 authentication
        "oauth2_provider.contrib.rest_framework.OAuth2Authentication",
        # JWT authentication
        "backend.utils.authentication.UniversalJWTAuthentication",
        # Django's built-in session authentication
        "rest_framework.authentication.SessionAuthentication",
        # Basic authentication
        "rest_framework.authentication.BasicAuthentication",
    ),
    # Global default search configuration
    "DEFAULT_FILTER_BACKENDS": (
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.OrderingFilter",
    ),
    # Global default pagination configuration
    "DEFAULT_PAGINATION_CLASS": "backend.utils.pagination.UniversalPageNumberPagination",
    # Global default exception handler configuration
    "EXCEPTION_HANDLER": "backend.utils.exceptions.unified_exception_handler",
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=30),  # Set access token expiration time
    "REFRESH_TOKEN_LIFETIME": timedelta(days=60),  # Set refresh token expiration time
}

OAUTH2_PROVIDER = {
    "ACCESS_TOKEN_EXPIRE_SECONDS": 36000,
    "AUTHORIZATION_CODE_EXPIRE_SECONDS": 600,
    "REFRESH_TOKEN_EXPIRE_SECONDS": 36000,
    "ROTATE_REFRESH_TOKENS": True,
}

OAUTH2_PROVIDER_APPLICATION_MODEL = "application.Application"

SPECTACULAR_SETTINGS = {
    "TITLE": "LingX Chat DB",
    "DESCRIPTION": "LingX Chat DB",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
}

LANGUAGE_CODE = "en-us"

TIME_ZONE = "Asia/Shanghai"

USE_I18N = True

USE_TZ = False

MEDIA_URL = "/media/"
STATIC_URL = "/static/"

MEDIA_ROOT = os.path.join(BASE_DIR, "media")
STATIC_ROOT = os.path.join(BASE_DIR, "static")

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "info_file": {
            "level": "INFO",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": os.path.join(BASE_DIR, "logs/info.log"),
            "maxBytes": 1024 * 1024 * 5,  # 5 MB
            "backupCount": 5,
            "formatter": "verbose",
        },
        "warning_file": {
            "level": "WARNING",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": os.path.join(BASE_DIR, "logs/warning.log"),
            "maxBytes": 1024 * 1024 * 5,  # 5 MB
            "backupCount": 5,
            "formatter": "verbose",
        },
        "error_file": {
            "level": "ERROR",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": os.path.join(BASE_DIR, "logs/error.log"),
            "maxBytes": 1024 * 1024 * 5,  # 5 MB
            "backupCount": 5,
            "formatter": "verbose",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["error_file"],
            "level": "ERROR",
            "propagate": True,
        },
        "django.request": {
            "handlers": ["error_file"],
            "level": "ERROR",
            "propagate": True,
        },
        "django.db.backends": {
            "handlers": ["error_file"],
            "level": "ERROR",
            "propagate": True,
        },
        "django-celery": {
            "handlers": ["info_file", "error_file"],
            "level": "INFO",
            "propagate": False,
        },
    },
}
