import os

ALLOWED_HOSTS = ["*"]
CORS_ALLOW_ALL_ORIGINS = True
WEB_DOMAIN = os.getenv("WEB_DOMAIN")
CSRF_TRUSTED_ORIGINS = []
