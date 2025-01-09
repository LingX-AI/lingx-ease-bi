from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from backend.apps.application.models import Application
from backend.apps.core.models import BaseModel


class CustomUserManager(BaseUserManager):
    def _create_user(self, username, password, **extra_fields):
        if not username:
            raise ValueError("请输入username")
        if not password:
            raise ValueError("请填入密码")
        user = self.model(username=username, **extra_fields)
        # 普通用户的openid为username
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username, password, **extra_fields):
        extra_fields.setdefault("is_superuser", False)
        extra_fields.setdefault("is_staff", False)
        return self._create_user(username, password, **extra_fields)

    def create_superuser(self, username, password, **extra_fields):
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_staff", True)
        return self._create_user(username, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin, BaseModel):
    app = models.ManyToManyField(Application, null=True, related_name="users", help_text="Application")
    app_user_id = models.CharField(max_length=64, blank=True, null=True, help_text="Application User ID")
    username = models.CharField(max_length=64, null=True, blank=True, help_text="Username in app")
    email = models.EmailField(max_length=64, null=False, blank=False, unique=True, help_text="Email in app")
    mobile = models.CharField(max_length=64, null=True, blank=True, help_text="Mobile in app")

    is_staff = models.BooleanField(default=False, help_text="Is staff?")

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return self.username or self.app_user_id
