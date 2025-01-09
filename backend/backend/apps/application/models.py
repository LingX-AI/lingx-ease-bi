import enum
import uuid

from django.db import models
from oauth2_provider.models import AbstractApplication

from backend.apps.core.models import BaseModel


class SystemConfiguration(models.Model):
    pass


class RAGMethod(models.TextChoices):
    EMBEDDING = "embedding", "Embedding"
    LLM = "llm", "LLM"


def _get_default_agent_configuration():
    return {
        "rag_enabled": True,
        "rag_method": RAGMethod.LLM,
    }


class Application(AbstractApplication, BaseModel):
    # id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    description = models.TextField("Description", help_text="Application description")
    database_configuration = models.JSONField(
        "Database Configuration", help_text="Database configuration information for app"
    )
    # rag_method: embedding/llm,if not set, use llm
    agent_configuration = models.JSONField(
        "Agent Configuration",
        default=_get_default_agent_configuration,
        help_text="Agent configuration information for app",
    )

    def __str__(self):
        return f"{self.name}"


class ApplicationTable(BaseModel):
    application = models.ForeignKey(
        Application, on_delete=models.CASCADE, related_name="tables"
    )
    name = models.CharField("Table Name", max_length=128, blank=False, null=False)
    comment = models.CharField("Comment", max_length=1024, blank=True, null=True)
    original_ai_comment = models.CharField(
        "Original AI comment", max_length=1024, blank=True, null=True
    )
    ai_comment = models.CharField("AI comment", max_length=1024, blank=True, null=True)

    def __str__(self):
        return f"{self.name}"


class ApplicationTableColumn(BaseModel):
    table = models.ForeignKey(
        ApplicationTable, on_delete=models.CASCADE, related_name="columns"
    )
    name = models.CharField("Column Name", max_length=64, blank=False, null=False)
    key = models.CharField("Column Key", max_length=16, blank=False, null=False)
    type = models.CharField("Column Data Type", max_length=32, blank=False, null=False)
    default = models.JSONField("Default", null=True, blank=True)
    comment = models.CharField("Comment", max_length=1024, blank=True, null=True)
    nullable = models.CharField("Nullable", default="YES", blank=True, null=True)
    original_ai_comment = models.CharField(
        "Original AI comment", max_length=1024, blank=True, null=True
    )
    ai_comment = models.CharField("AI comment", max_length=1024, blank=True, null=True)

    def __str__(self):
        return f"{self.name}"


class ApplicationPrompt(BaseModel):
    application = models.OneToOneField(
        Application, on_delete=models.CASCADE, related_name="prompts"
    )
    question_clean_prompt = models.TextField(
        "Question clean prompt", blank=True, null=True
    )
    column_comment_prompt = models.TextField(
        "Column comment prompt", blank=True, null=True
    )
    question_builder_prompt = models.TextField(
        "Question builder prompt", blank=True, null=True
    )
    schema_rag_prompt = models.TextField(
        "Retrieve schema  prompt", blank=True, null=True
    )
    sql_generator_prompt = models.TextField(
        "SQL generator prompt", blank=True, null=True
    )


class ApplicationDatabaseDocument(BaseModel):
    application = models.ForeignKey(
        Application, on_delete=models.CASCADE, related_name="documents"
    )
    document_name = models.CharField(
        "Document name", max_length=128, blank=False, null=False
    )
    document_path = models.CharField(
        "Document file path", max_length=256, blank=False, null=False
    )
    content_type = models.CharField(
        "Content type", max_length=128, blank=False, null=False
    )
    document_size = models.IntegerField("Document file size", blank=False, null=False)
    token_count = models.IntegerField("Document token count", blank=True, null=True)
    character_count = models.IntegerField(
        "Document character count", blank=True, null=True
    )


class FineTuningExample(BaseModel):
    application = models.ForeignKey(
        Application, on_delete=models.CASCADE, related_name="fine_tuning_examples"
    )
    question = models.CharField("question", max_length=1024, blank=False, null=False)
    sql = models.CharField("sql", max_length=1024, blank=False, null=False)

    class Meta:
        unique_together = ("application", "question")

    def __str__(self):
        return f"{self.application.name} 's fine-tuning example"


class FineTuningModel(BaseModel):
    application = models.ForeignKey(
        Application, on_delete=models.CASCADE, related_name="fine_tuning_models"
    )
    model_name = models.CharField("model_name", max_length=256, blank=False, null=False)
    description = models.TextField("description", blank=True, null=True)

    def __str__(self):
        return self.model_name


class ApplicationSuggestedQuestion(BaseModel):
    application = models.ForeignKey(
        Application, on_delete=models.CASCADE, related_name="suggested_questions"
    )
    question = models.CharField(
        "Suggested Question",
        max_length=1024,
        help_text="A suggested question to be displayed on the homepage",
    )
    display_order = models.IntegerField(
        "Display Order",
        default=0,
        help_text="Order in which questions should be displayed",
    )

    class Meta:
        ordering = ["display_order", "created_at"]
        verbose_name = "Application Suggested Question"
        verbose_name_plural = "Application Suggested Questions"

    def __str__(self):
        return f"{self.application.name} - {self.question}"
