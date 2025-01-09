from backend.apps.core.serializers import BaseSerializer
from oauth2_provider.models import Application

from .models import User


class ApplicationSerializer(BaseSerializer):

    class Meta:
        model = Application
        include = ("id", "client_id", "name")


class UserSerializer(BaseSerializer):
    app = ApplicationSerializer()

    class Meta:
        model = User
        fields = "__all__"
