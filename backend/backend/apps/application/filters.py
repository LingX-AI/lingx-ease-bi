from django_filters import rest_framework as filters

from backend.apps.core.filters import BaseFilter

from .models import (
    Application,
    ApplicationDatabaseDocument,
    ApplicationPrompt,
    ApplicationSuggestedQuestion,
    ApplicationTable,
    ApplicationTableColumn,
    FineTuningExample,
    FineTuningModel,
)


class ApplicationFilter(BaseFilter):
    name = filters.CharFilter(field_name="name", lookup_expr="icontains")

    class Meta:
        model = Application
        fields = []


class ApplicationTableFilter(BaseFilter):
    name = filters.CharFilter(field_name="name", lookup_expr="icontains")

    class Meta:
        model = ApplicationTable
        fields = ["application", "is_enabled"]


class ApplicationTableColumnFilter(BaseFilter):
    name = filters.CharFilter(field_name="name", lookup_expr="icontains")

    class Meta:
        model = ApplicationTableColumn
        fields = ["table", "is_enabled"]


class ApplicationPromptFilter(BaseFilter):
    class Meta:
        model = ApplicationPrompt
        fields = ["application", "is_enabled"]


class ApplicationDatabaseDocumentFilter(BaseFilter):
    class Meta:
        model = ApplicationDatabaseDocument
        fields = ["application", "document_name"]


class FineTuningExampleFilter(BaseFilter):
    question = filters.CharFilter(field_name="question", lookup_expr="icontains")
    created_at_start = filters.DateTimeFilter(
        field_name="created_at", lookup_expr="gte"
    )
    created_at_end = filters.DateTimeFilter(field_name="created_at", lookup_expr="lte")

    class Meta:
        model = FineTuningExample
        fields = ["created_at_start", "created_at_end", "application"]


class FineTuningModelFilter(BaseFilter):
    class Meta:
        model = FineTuningModel
        fields = ["application"]


class ApplicationSuggestedQuestionFilter(BaseFilter):
    class Meta:
        model = ApplicationSuggestedQuestion
        fields = [
            "application",
        ]
