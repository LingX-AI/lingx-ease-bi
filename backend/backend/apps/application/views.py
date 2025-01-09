import csv
import io
import json
from datetime import datetime

import requests
from django.db import transaction
from django.http import HttpResponse
from rest_framework import status
from rest_framework.decorators import action, api_view
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from backend.apps.chat.core.agents.database_query_agent import (
    DatabaseQueryAgent,
)
from backend.apps.chat.core.agents.sql_generator_agent import (
    SQLGeneratorAgent,
)
from backend.apps.chat.core.prompts import (
    question_prompt,
    sql_generator_prompt,
)
from backend.settings.env import ENV
from backend.utils.llm import create_application_schema, get_llm_tokens
from backend.utils.viewset import BaseUndeletedModelViewSet

from .core.agents.column_comment_agent import Agent
from .core.agents.question_builder_agent import Agent as QuestionBuilderAgent
from .core.database import DatabaseExecutor
from .core.prompts import (
    column_comment_prompt,
    question_builder_prompt,
    schema_rag_prompt,
)
from .filters import (
    ApplicationDatabaseDocumentFilter,
    ApplicationFilter,
    ApplicationPromptFilter,
    ApplicationSuggestedQuestionFilter,
    ApplicationTableColumnFilter,
    ApplicationTableFilter,
    FineTuningExampleFilter,
    FineTuningModelFilter,
)
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
from .serializers import (
    ApplicationDatabaseDocumentSerializer,
    ApplicationPromptSerializer,
    ApplicationSerializer,
    ApplicationSuggestedQuestionSerializer,
    ApplicationTableColumnSerializer,
    ApplicationTableSerializer,
    FineTuningExampleSerializer,
    FineTuningModelSerializer,
)
from .utils import execute_remote_command, json_list_to_ddl, stream_command_output


class ApplicationViewSet(BaseUndeletedModelViewSet):
    """
    Application View
    """

    queryset = Application.objects.filter()
    serializer_class = ApplicationSerializer
    filterset_class = ApplicationFilter
    permission_classes = (IsAdminUser,)
    pagination_class = None

    @action(methods=["post"], detail=True)
    def create_database_tables(self, request, pk=None):
        application = self.get_object()
        database_executor = DatabaseExecutor(application.database_configuration)
        tables = database_executor.create_tables()

        existing_tables = {
            table.name: table
            for table in ApplicationTable.objects.filter(application=application)
        }
        existing_columns = {
            table.id: {
                col.name: col
                for col in ApplicationTableColumn.objects.filter(table=table)
            }
            for table in existing_tables.values()
        }

        def update_or_create_table(table_data, existing_table=None):
            """
            Update or create an ApplicationTable object.
            """
            ai_comment = (
                existing_table.ai_comment
                if existing_table
                else table_data.get("comment")
            )
            defaults = {"comment": table_data["comment"], "ai_comment": ai_comment}
            return ApplicationTable.objects.update_or_create(
                application=application,
                name=table_data["table_name"],
                defaults=defaults,
            )[0]

        def update_or_create_columns(table, table_data):
            """
            Update or create ApplicationTableColumn objects for a table.
            """
            table_cols = existing_columns.get(table.id, {})
            column_names = set()

            for column in table_data.get("columns", []):
                column_instance = table_cols.get(column["name"])
                column["ai_comment"] = (
                    column_instance.ai_comment
                    if column_instance
                    else column.get("comment")
                )
                defaults = {
                    "key": column["key"],
                    "type": column["type"],
                    "default": column["default"],
                    "comment": column["comment"],
                    "ai_comment": column["ai_comment"],
                    "nullable": column["nullable"],
                }

                ApplicationTableColumn.objects.update_or_create(
                    table=table, name=column["name"], defaults=defaults
                )
                column_names.add(column["name"])

            # Delete columns that are not in the new column list
            ApplicationTableColumn.objects.filter(table=table).exclude(
                name__in=column_names
            ).delete()

        def cleanup_removed_tables(new_table_names):
            """
            Cleanup ApplicationTable objects that are no longer present in the new table list.
            """
            current_table_names = set(existing_tables.keys())
            for table_name in current_table_names - new_table_names:
                existing_tables[table_name].delete()

        with transaction.atomic():
            # Update or create tables and columns
            for table_data in tables:
                existing_table = existing_tables.get(table_data["table_name"])
                table = update_or_create_table(table_data, existing_table)
                update_or_create_columns(table, table_data)

            # Delete tables that are not in the new table list
            new_table_names = {table["table_name"] for table in tables}
            cleanup_removed_tables(new_table_names)

        application_tables = ApplicationTable.objects.filter(application=application)
        response_data = ApplicationTableSerializer(application_tables, many=True).data
        return Response(response_data)

    @action(methods=["get"], detail=True)
    def export_database_schema(self, request, pk=None):
        export_type = request.GET.get("type")
        schema, _ = create_application_schema(application_id=pk)
        if export_type == "ddl":
            ddl_list, _ = json_list_to_ddl(schema)
            return Response(ddl_list)
        return Response(schema)

    @action(methods=["put"], detail=True)
    def enable_disable_rag(self, request, pk=None):
        is_enabled = request.data.get("is_enabled")
        application = self.get_object()
        agent_configuration = application.agent_configuration
        agent_configuration["rag_enabled"] = is_enabled
        application.agent_configuration = agent_configuration
        application.save()
        return Response(
            {
                "id": application.id,
                "agent_configuration": agent_configuration,
            }
        )


class ApplicationTableViewSet(BaseUndeletedModelViewSet):
    """
    Application Database Table View
    """

    queryset = ApplicationTable.objects.filter()
    serializer_class = ApplicationTableSerializer
    filterset_class = ApplicationTableFilter
    permission_classes = (IsAdminUser,)
    pagination_class = None

    @action(methods=["get"], detail=True)
    def get_ai_comment(self, request, pk=None):
        table: ApplicationTable = self.get_object()
        app_description = table.application.description
        tables = [
            item.name
            for item in table.application.tables.filter(
                is_deleted=False, is_enabled=True
            )
        ]
        table_dict = {
            "table": table.name,
            "comment": table.comment,
            "columns": [],
        }
        for column in table.columns.all():
            table_dict["columns"].append(
                {
                    "name": column.name,
                    "key": column.key,
                    "type": column.type,
                    "default": column.default,
                    "comment": column.comment,
                    "nullable": column.nullable,
                }
            )
        table_str = json.dumps(table_dict)
        agent = Agent()
        _prompt = table.application.prompts.column_comment_prompt
        _result = agent.run(table_str, app_description, tables, _prompt)
        if _result:
            return Response(json.loads(_result))
        return Response({"code": 1, "msg": "Failed to generate AI comment"})


class ApplicationTableColumnViewSet(BaseUndeletedModelViewSet):
    """
    Application Table Column View
    """

    queryset = ApplicationTableColumn.objects.filter()
    serializer_class = ApplicationTableColumnSerializer
    filterset_class = ApplicationTableColumnFilter
    permission_classes = (IsAdminUser,)
    pagination_class = None

    @action(methods=["put"], detail=False)
    def batch_update(self, request):
        columns = request.data
        column_ids = [column.get("id") for column in columns]
        application_table_columns = ApplicationTableColumn.objects.filter(
            id__in=column_ids
        )
        column_instance_list = []
        with transaction.atomic():
            for item in columns:
                column = application_table_columns.filter(id=item.get("id")).first()
                if column:
                    column.ai_comment = item.get("ai_comment") or ""
                    column.original_ai_comment = item.get("original_ai_comment") or ""
                    column_instance_list.append(column)
            ApplicationTableColumn.objects.bulk_update(
                column_instance_list, ["ai_comment", "original_ai_comment"]
            )
        return Response()


class ApplicationPromptViewSet(BaseUndeletedModelViewSet):
    """
    Application Prompt View
    """

    queryset = ApplicationPrompt.objects.filter()
    serializer_class = ApplicationPromptSerializer
    filterset_class = ApplicationPromptFilter
    permission_classes = (IsAdminUser,)
    pagination_class = None

    @action(methods=["get"], detail=False)
    def get_prompt(self, request) -> Response:
        application_id = request.query_params.get("application_id")
        application_prompt_instance = ApplicationPrompt.objects.filter(
            application_id=application_id
        ).first()

        data = {
            "application_id": application_id,
            "question_clean_prompt": question_prompt.prompt,
            "column_comment_prompt": column_comment_prompt.prompt,
            "question_builder_prompt": question_builder_prompt.prompt,
            "schema_rag_prompt": schema_rag_prompt.prompt,
            "sql_generator_prompt": sql_generator_prompt.prompt,
        }

        if application_prompt_instance:
            for field in [
                "question_clean_prompt",
                "column_comment_prompt",
                "question_builder_prompt",
                "sql_generator_prompt",
                "schema_rag_prompt",
            ]:
                custom_value = getattr(application_prompt_instance, field)
                if custom_value:
                    data[field] = custom_value

        return Response(data)

    @action(methods=["put"], detail=False)
    def update_prompt(self, request):
        application_id = request.data.get("application_id")

        column_comment_prompt = request.data.get("column_comment_prompt", "")
        question_builder_prompt = request.data.get("question_builder_prompt", "")
        sql_generator_prompt = request.data.get("sql_generator_prompt", "")
        question_clean_prompt = request.data.get("question_clean_prompt", "")
        schema_rag_prompt = request.data.get("schema_rag_prompt", "")
        application_prompt_instance = ApplicationPrompt.objects.filter(
            application_id=application_id
        ).first()
        if application_prompt_instance:
            application_prompt_instance.column_comment_prompt = (
                column_comment_prompt
                if column_comment_prompt
                else application_prompt_instance.column_comment_prompt
            )
            application_prompt_instance.question_builder_prompt = (
                question_builder_prompt
                if question_builder_prompt
                else application_prompt_instance.question_builder_prompt
            )
            application_prompt_instance.sql_generator_prompt = (
                sql_generator_prompt
                if sql_generator_prompt
                else application_prompt_instance.sql_generator_prompt
            )
            application_prompt_instance.question_clean_prompt = (
                question_clean_prompt
                if question_clean_prompt
                else application_prompt_instance.question_clean_prompt
            )
            application_prompt_instance.schema_rag_prompt = (
                schema_rag_prompt
                if schema_rag_prompt
                else application_prompt_instance.schema_rag_prompt
            )
            application_prompt_instance.save()
            return Response(
                ApplicationPromptSerializer(application_prompt_instance).data
            )
        application_prompt_instance = ApplicationPrompt.objects.create(
            application_id=application_id,
            column_comment_prompt=column_comment_prompt,
            question_builder_prompt=question_builder_prompt,
            sql_generator_prompt=sql_generator_prompt,
        )
        return Response(ApplicationPromptSerializer(application_prompt_instance).data)


class ApplicationDatabaseDocumentViewSet(BaseUndeletedModelViewSet):
    """
    Application Database RAG Document View
    """

    queryset = ApplicationDatabaseDocument.objects.filter()
    serializer_class = ApplicationDatabaseDocumentSerializer
    filterset_class = ApplicationDatabaseDocumentFilter
    permission_classes = (IsAdminUser,)
    pagination_class = None

    def _get_app_code(self, application_id):
        try:
            application = Application.objects.get(id=application_id)
        except Application.DoesNotExist:
            return None
        return (
            application.database_configuration.get("db_name").replace(" ", "_").lower()
        )

    @action(methods=["post"], detail=False)
    def create_embed(self, request):
        application_id = request.data.get("application_id")
        app_code = self._get_app_code(application_id)
        if not app_code:
            return Response({"code": 1, "msg": "Application not found"})
        schema, _ = create_application_schema(application_id)
        document_instances = []
        documents = []
        request_payload = {"app_code": app_code}
        for item in schema:
            file_buffer = io.StringIO()
            text = json.dumps(
                item,
                separators=(",", ":"),
                ensure_ascii=False,
            )
            file_buffer.write(text)
            file_buffer.seek(0)
            try:
                url = f"{ENV.EMBEDDING_SERVICE_ENDPOINT}/upload"
                filename = f"{app_code}_db_doc_{item.get('table')}.txt"
                files = {"file": (filename, file_buffer, "text/plain")}
                response = requests.post(url, files=files, data=request_payload)
                if response.status_code == 200:
                    res_data = response.json().get("data")
                    document = {
                        "application_id": application_id,
                        "document_name": res_data.get("file_name"),
                        "document_path": res_data.get("file_path"),
                        "content_type": res_data.get("content_type"),
                        "document_size": res_data.get("file_size"),
                        "character_count": len(text),
                        "token_count": get_llm_tokens(text),
                    }
                    documents.append(document)
                    document_instances.append(ApplicationDatabaseDocument(**document))
                else:
                    return Response({"code": 1, "msg": "Failed to create embedding"})
            except Exception as e:
                return Response({"code": 1, "msg": str(e)})
            finally:
                file_buffer.close()
        try:
            url = f"{ENV.EMBEDDING_SERVICE_ENDPOINT}/create_embed"
            response = requests.post(url, json=request_payload)
            if response.status_code != 200:
                return Response({"code": 1, "msg": "Failed to create embedding"})
        except Exception as e:
            return Response({"code": 1, "msg": str(e)})
        with transaction.atomic():
            ApplicationDatabaseDocument.objects.filter(
                application_id=application_id
            ).delete()
            ApplicationDatabaseDocument.objects.bulk_create(document_instances)
        return Response(
            ApplicationDatabaseDocumentSerializer(document_instances, many=True).data
        )

    @action(methods=["post"], detail=False)
    def retrieval_embed(self, request):
        application_id = request.data.get("application_id")
        question = request.data.get("text", None)
        if not question:
            return Response(
                {"code": 1, "msg": "Query parameter 'text' is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        app_code = self._get_app_code(application_id)
        if not app_code:
            return Response({"code": 1, "msg": "Application not found"})
        url = f"{ENV.EMBEDDING_SERVICE_ENDPOINT}/retrieval_embed"
        request_payload = {
            "app_code": self._get_app_code(application_id),
            "question": question,
        }
        response = requests.post(url, json=request_payload)
        if response.status_code != 200:
            return Response({"code": 1, "msg": "Failed to create embedding"})
        res_data = response.json().get("data")
        return Response(res_data)


class FineTuningExampleViewSet(BaseUndeletedModelViewSet):
    """
    Fine-tuning Example View
    """

    queryset = FineTuningExample.objects.filter()
    serializer_class = FineTuningExampleSerializer
    filterset_class = FineTuningExampleFilter
    permission_classes = (IsAdminUser,)

    @action(methods=["post"], detail=False)
    def batch_delete(self, request):
        ids = request.data.get("ids")
        if ids:
            FineTuningExample.objects.filter(id__in=ids).delete()
        return Response()

    @action(methods=["post"], detail=False)
    def create_questions(self, request):
        application_id = request.data.get("application_id")
        question_count = request.data.get("question_count", 10)
        agent = QuestionBuilderAgent(application_id)
        _result = agent.run(question_count=question_count)
        if _result:
            return Response(json.loads(_result))
        return Response({"code": 1, "msg": "Failed to generate questions"})

    @action(methods=["post"], detail=False)
    def create_sql(self, request):
        application_id = request.data.get("application_id")
        application = Application.objects.get(id=application_id)
        question = request.data.get("question")
        sql_generator_agent = SQLGeneratorAgent(application=application)
        return Response({"sql": sql_generator_agent.run(question)})

    @action(methods=["post"], detail=False)
    def execute_sql(self, request):
        application_id = request.data.get("application_id")
        question = request.data.get("question")
        sql = request.data.get("sql")
        database_configuration = Application.objects.get(
            id=application_id
        ).database_configuration
        start_time = datetime.now()
        agent = DatabaseQueryAgent(database_configuration=database_configuration)
        end_time = datetime.now()
        time_difference = end_time - start_time
        query_result, _, error_msgs = agent.run(question, [sql])
        error_msg = error_msgs if error_msgs else None
        return Response(
            {
                "result": json.loads(query_result or "[]"),
                "error": error_msg,
                "duration": time_difference.total_seconds(),
            }
        )

    @action(methods=["get"], detail=False)
    def export_example(self, request):
        # file_type: json or csv
        file_type = request.query_params.get("file_type", "json")
        application_id = request.query_params.get("application_id")
        queryset = FineTuningExample.objects.filter(
            application_id=application_id, is_deleted=False
        ).values("question", "sql")
        if file_type == "json":
            response = HttpResponse(
                json.dumps(list(queryset), ensure_ascii=False, indent=4),
                content_type="application/json",
            )
            response["Content-Disposition"] = (
                f"attachment; filename=examples_{application_id}.json"
            )
            return response
        elif file_type == "csv":
            response = HttpResponse(content_type="text/csv")
            response["Content-Disposition"] = (
                f"attachment; filename=examples_{application_id}.csv"
            )
            writer = csv.writer(response)
            writer.writerow(["question", "sql"])
            for item in queryset:
                writer.writerow([item["question"], item["sql"]])
            return response
        else:
            return Response({"code": 1, "msg": "Invalid file type"})

    @action(methods=["get"], detail=False)
    def get_standard_fine_tuning_example(self, request):
        application_id = request.query_params.get("application_id")
        application = Application.objects.get(id=application_id)
        queryset = FineTuningExample.objects.filter(
            application_id=application_id, is_deleted=False
        ).values("question", "sql")
        SQL_Prompt = application.prompts.sql_generator_prompt
        data = [
            {
                "instruction": item["question"],
                "input": "",
                "output": item["sql"],
                "system": f"{SQL_Prompt}",
            }
            for item in queryset
        ]
        return Response(data)

    @action(methods=["get"], detail=False)
    def get_fine_tuning_config(self, request):
        with open(
            "backend/apps/application/core/fine_tuning/config.yaml"
        ) as file:
            config = file.read()
        return Response({"config": config})

    @action(methods=["get"], detail=False)
    def get_train_webui_url(self, request):
        webui_url = ENV.FINE_TUNE_SERVER_WEB_URL
        if not webui_url:
            return Response({"error": "Missing required parameters"}, status=400)
        return Response({"webui_url": webui_url})


class FineTuningModelViewSet(BaseUndeletedModelViewSet):
    queryset = FineTuningModel.objects.filter(is_deleted=False).order_by('created_at')
    serializer_class = FineTuningModelSerializer
    filterset_class = FineTuningModelFilter
    permission_classes = (IsAdminUser,)
    pagination_class = None

    @action(methods=["put"], detail=True)
    def enable_disable_model(self, request, pk=None):
        model_instance = self.get_object()
        is_enabled = request.data.get("is_enabled")
        with transaction.atomic():
            FineTuningModel.objects.filter(
                application=model_instance.application
            ).update(is_enabled=False)
            model_instance.is_enabled = is_enabled
            model_instance.save()

        return Response({"code": 0, "msg": "Success"})


@api_view(http_method_names=["POST"])
def convert_model(request):
    command = request.data.get("command")
    if not all(
        [
            ENV.FINE_TUNE_SERVER_HOST,
            ENV.FINE_TUNE_SERVER_USERNAME,
            ENV.FINE_TUNE_SERVER_PASSWORD,
            command,
        ]
    ):
        return Response({"code": 1, "msg": "Missing required parameters"})

    host = str(ENV.FINE_TUNE_SERVER_HOST or "")
    username = str(ENV.FINE_TUNE_SERVER_USERNAME or "")
    password = str(ENV.FINE_TUNE_SERVER_PASSWORD or "")

    exit_status = execute_remote_command(
        host=host,
        username=username,
        password=password,
        command=command,
    )

    if exit_status != 0:
        return Response({"code": 1, "msg": "Failed to convert model"})

    return Response({"code": 0, "msg": "Success"})


@api_view(http_method_names=["POST"])
def deployment_model(request):
    application_id = request.data.get("application_id")
    model_name = request.data.get("model_name")
    command = request.data.get("command")

    if not all(
        [
            ENV.FINE_TUNE_SERVER_HOST,
            ENV.FINE_TUNE_SERVER_USERNAME,
            ENV.FINE_TUNE_SERVER_PASSWORD,
            command,
        ]
    ):
        return Response({"code": 1, "msg": "Missing required parameters"})

    host = str(ENV.FINE_TUNE_SERVER_HOST or "")
    username = str(ENV.FINE_TUNE_SERVER_USERNAME or "")
    password = str(ENV.FINE_TUNE_SERVER_PASSWORD or "")

    exit_status = execute_remote_command(
        host=host,
        username=username,
        password=password,
        command=command,
    )

    if exit_status != 0:
        return Response({"code": 1, "msg": "Failed to deploy model"})

    _application = Application.objects.get(id=application_id)

    model_name = model_name if ":" in model_name else f"{model_name}:latest"

    FineTuningModel.objects.create(
        application=_application,
        model_name=model_name,
        description=f"The Ollama model of {_application.name}",
    )

    return Response({"code": 0, "msg": "Success"})


class ApplicationSuggestedQuestionViewSet(BaseUndeletedModelViewSet):
    """
    Application Suggested Question View
    """

    queryset = ApplicationSuggestedQuestion.objects.filter(is_deleted=False)
    serializer_class = ApplicationSuggestedQuestionSerializer
    filterset_class = ApplicationSuggestedQuestionFilter
    permission_classes = (IsAdminUser,)
    pagination_class = None

    def get_permissions(self):
        if self.action == 'list':
            return []
        return super().get_permissions()

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(methods=["post"], detail=False)
    def batch_update(self, request):
        application_id = request.data.get("application_id")
        questions = request.data.get("questions")
        ApplicationSuggestedQuestion.objects.filter(
            application_id=application_id
        ).delete()
        ApplicationSuggestedQuestion.objects.bulk_create(
            [
                ApplicationSuggestedQuestion(
                    application_id=application_id, question=question
                )
                for question in questions
            ]
        )
        return Response({"code": 0, "msg": "Success"})
