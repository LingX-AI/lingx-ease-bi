from rest_framework import serializers

from backend.apps.core.serializers import BaseSerializer

from .models import Message


class MessageSerializer(BaseSerializer):
    completed_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)

    class Meta:
        model = Message

        exclude = (
            "received_sql_list",
            "valid_sql",
            "query_result",
            "is_deleted",
            "is_enabled",
        )


class MessageDetailSerializer(MessageSerializer):
    class Meta:
        model = Message
        exclude = (
            "received_sql_list",
            "valid_sql",
            "is_deleted",
        )
