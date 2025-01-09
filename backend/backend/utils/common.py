import os

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.core.files.storage import FileSystemStorage
from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken

from backend.apps.authentication.models import User
from backend.utils.exceptions import ErrorInfo


def handle_uploaded_file(file, path="media/"):
    # Ensure upload directory exists
    actual_path = os.path.join(settings.MEDIA_ROOT, path)
    if not os.path.exists(actual_path):
        os.makedirs(actual_path)

    # Create FileSystemStorage instance with 'path' as location
    fs = FileSystemStorage(location=actual_path)

    # Save file and return relative path
    file_path = fs.save(file.name, file)
    return f"{path}{file_path}"


class AuthenticationService:
    """
    Authentication service
    """

    @classmethod
    def verify_user(cls, user: User, password: str):
        """
        Verify user
        :param user: User object
        :param password: Password
        :return:
        """
        if not user:
            raise PermissionDenied(
                detail=ErrorInfo.USER_NOT_FOUND.value, code=status.HTTP_404_NOT_FOUND
            )
        if not user.is_enabled:
            raise PermissionDenied(
                detail=ErrorInfo.USER_DISABLED.value, code=status.HTTP_403_FORBIDDEN
            )
        if not user.check_password(password):
            raise PermissionDenied(
                detail=ErrorInfo.PASSWORD_INCORRECT.value,
                code=status.HTTP_403_FORBIDDEN,
            )

    @staticmethod
    def login(email: str, password: str):
        """
        Login
        :param email: Email
        :param password: Password
        :return:
        """
        email = email.strip()
        user = User.objects.filter(email=email, is_deleted=False).first()
        # Verify user
        if not user:
            raise PermissionDenied(
                detail=ErrorInfo.USER_NOT_FOUND.value, code=status.HTTP_404_NOT_FOUND
            )
        AuthenticationService.verify_user(user=user, password=password)
        refresh = RefreshToken.for_user(user)
        access = AccessToken.for_user(user)
        data = {
            "id": user.id,
            "refresh": str(refresh),
            "access": str(access),
            "username": user.username,
            "email": user.email,
        }
        return data, user

    @staticmethod
    def chat_auth(username: str, password: str):
        """
        Login
        :param username: Username
        :param password: Password
        :return:
        """
        user = User.objects.filter(username=username, is_deleted=False).first()
        if not user:
            raise PermissionDenied(
                detail=ErrorInfo.USER_NOT_FOUND.value, code=status.HTTP_404_NOT_FOUND
            )
        if not user.check_password(password):
            raise PermissionDenied(
                detail=ErrorInfo.PASSWORD_INCORRECT.value,
                code=status.HTTP_403_FORBIDDEN,
            )
        access = AccessToken.for_user(user)
        data = {
            "id": user.id,
            "access_token": str(access),
            "username": user.username,
        }
        return data

    @staticmethod
    def get_user_by_token(token: str):
        """
        Get user by token
        :param token: Token string
        :return:
        """
        try:
            jwt_authentication = JWTAuthentication()
            validated_token = jwt_authentication.get_validated_token(token.encode())
            user = jwt_authentication.get_user(validated_token)
        except Exception as e:
            raise PermissionDenied(
                detail=ErrorInfo.INVALID_TOKEN.value, code=status.HTTP_403_FORBIDDEN
            )
        return user
