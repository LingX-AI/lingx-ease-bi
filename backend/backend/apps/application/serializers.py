from backend.apps.core.serializers import BaseSerializer

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


class ApplicationSerializer(BaseSerializer):

    class Meta:
        model = Application
        fields = "__all__"


class ApplicationTableSerializer(BaseSerializer):

    class Meta:
        model = ApplicationTable
        fields = "__all__"


class ApplicationTableColumnSerializer(BaseSerializer):

    class Meta:
        model = ApplicationTableColumn
        fields = "__all__"


class ApplicationPromptSerializer(BaseSerializer):

    class Meta:
        model = ApplicationPrompt
        fields = "__all__"


class ApplicationDatabaseDocumentSerializer(BaseSerializer):

    class Meta:
        model = ApplicationDatabaseDocument
        fields = "__all__"


class FineTuningExampleSerializer(BaseSerializer):

    class Meta:
        model = FineTuningExample
        fields = "__all__"


class FineTuningModelSerializer(BaseSerializer):

    class Meta:
        model = FineTuningModel
        fields = "__all__"


class ApplicationSuggestedQuestionSerializer(BaseSerializer):

    class Meta:
        model = ApplicationSuggestedQuestion
        fields = "__all__"
