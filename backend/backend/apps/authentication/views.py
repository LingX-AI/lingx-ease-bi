import base64
import json

from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.debug import sensitive_post_parameters
from oauth2_provider.contrib.rest_framework import TokenHasReadWriteScope, TokenHasScope
from oauth2_provider.views.base import TokenView
from rest_framework import status
from rest_framework.decorators import (
    action,
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from rest_framework_simplejwt.tokens import AccessToken

from backend.apps.application.models import Application
from backend.settings import ENV
from backend.utils.common import AuthenticationService
from backend.utils.viewset import BaseUndeletedModelViewSet

from .filters import UserFilter
from .models import User
from .serializers import UserSerializer


class ChatAuthView(ViewSet):
    permission_classes = [TokenHasReadWriteScope]

    @action(
        methods=["POST"],
        detail=False,
        permission_classes=[],
    )
    def client_token(self, request, *args, **kwargs):
        application_id = request.data.get("application_id")
        application = Application.objects.get(id=application_id)
        request.data["grant_type"] = "client_credentials"
        auth_header = f"Basic {base64.b64encode(f'{application.client_id}:{application.client_secret}'.encode()).decode()}"
        request._request.META["HTTP_AUTHORIZATION"] = auth_header
        token_request = request._request
        token_request.POST = request.data
        token_request.method = "POST"
        del request._request.POST["application_id"]
        response = TokenView.as_view()(token_request)
        response_data = response.content.decode("utf-8")
        response_json = json.loads(response_data)
        return Response(response_json, status=status.HTTP_200_OK)

    @action(methods=["POST"], detail=False)
    def chat_auth(self, request):
        """
        Get chat token for a user in the application
        :param request:
        :return:
        """
        application = request.auth.application
        app_user_id = request.data.get("app_user_id")
        username = request.data.get("username", None)
        email = request.data.get("email", None)
        mobile = request.data.get("mobile", None)
        if not email:
            return Response(
                {"msg": "Email is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        user = User.objects.filter(
            app_user_id=app_user_id,
        ).first()
        if user:
            if application not in user.app.all():
                user.app.add(application)
        else:
            user = User.objects.create(
                app_user_id=app_user_id,
                email=email,
                username=username,
                mobile=mobile,
            )
            user.set_password(ENV.USER_DEFAULT_PASSWORD)
            user.save()
            user.app.add(application)

        access_token = AccessToken.for_user(user)
        data = {
            "id": user.id,
            "token_type": "Bearer",
            "access_token": str(access_token),
        }
        return Response(data, status=status.HTTP_200_OK)


class UserViewSet(BaseUndeletedModelViewSet):
    """
    User view
    """

    queryset = User.objects.filter(is_superuser=False, is_staff=False)
    serializer_class = UserSerializer
    filterset_class = UserFilter
    permission_classes = (IsAdminUser,)


@api_view(http_method_names=["POST"])
@authentication_classes([])
@permission_classes([])
def login(request):
    """
    Login
    :param request:
    :return:
    """
    email, password = request.data.get("email"), request.data.get("password")
    data, user = AuthenticationService.login(email, password)
    user.last_login = timezone.now()
    user.save()
    return Response(data, status=status.HTTP_200_OK)
