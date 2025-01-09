import uuid

from django.db import models

from backend.apps.authentication.models import User
from backend.apps.core.models import BaseModel


def generate_uuid():
    return str(uuid.uuid4())


class Message(BaseModel):
    application = models.ForeignKey(
        "application.Application",
        related_name="messages",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    user = models.ForeignKey(User, related_name="messages", on_delete=models.CASCADE)
    task_id = models.CharField(
        default=generate_uuid, editable=False, help_text="Message task id"
    )
    question = models.CharField(max_length=500, help_text="User's question")
    optimized_question = models.CharField(
        max_length=500, blank=True, null=True, help_text="Optimized question"
    )
    received_sql_list = models.JSONField(
        default=list, null=True, help_text="Generated SQL list by AI"
    )
    valid_sql = models.CharField(
        max_length=2000, blank=True, null=True, help_text="Valid SQL"
    )
    query_result = models.JSONField(
        default=list, null=True, help_text="SQL execution result"
    )
    answer = models.JSONField(
        default=dict, null=True, help_text="The final answer presented to the user"
    )
    completed_at = models.DateTimeField(
        null=True, help_text="The time when the answer is completed"
    )
    step_times = models.JSONField(
        null=True, default=dict, help_text="Time record for each step"
    )
    is_cancelled = models.BooleanField(
        default=False, help_text="Whether the message is cancelled"
    )

    def __str__(self):
        return f"Message {self.id} by {self.user}"
