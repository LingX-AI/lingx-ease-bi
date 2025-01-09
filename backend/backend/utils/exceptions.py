from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework.views import exception_handler
from rest_framework.response import Response
from enum import Enum


def unified_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if isinstance(exc, APIException):
        if exc.status_code in [401]:
            return Response({'msg': 'Login has expired. Please log in again.'}, status=exc.status_code)
        return Response({'code': 1, 'msg': str(exc.detail)}, status=status.HTTP_200_OK)

    return response


class ErrorInfo(Enum):
    # User information not found
    USER_NOT_FOUND = 'User information not found'
    # Current user has been disabled
    USER_DISABLED = 'Current user has been disabled'
    # Current user cannot be deleted
    USER_NOT_ALLOW_DELETE = 'Cannot delete user that is in use, you can disable the user instead'
    # User role is required
    USER_ROLE_REQUIRED = 'User role cannot be empty'
    # Role not found
    ROLE_NOT_FOUND = 'Role does not exist'
    # Password incorrect
    PASSWORD_INCORRECT = 'Login password is incorrect'
    # Old password incorrect
    OLD_PASSWORD_INCORRECT = 'Original password is incorrect'
    # New password cannot be the same as old password
    NEW_PASSWORD_CANNOT_BE_OLD_PASSWORD = 'New password cannot be the same as original password'
    # New password and old password are required
    NEW_PASSWORD_AND_OLD_PASSWORD_REQUIRED = 'New password and original password are required fields'
    # Invalid token
    INVALID_TOKEN = 'Invalid authentication token'
