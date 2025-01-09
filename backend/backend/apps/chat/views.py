import json
from datetime import datetime

from adrf.decorators import api_view
from asgiref.sync import sync_to_async
from django.db import transaction
from django.http import StreamingHttpResponse
from djangorestframework_camel_case.util import camelize
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from backend.apps.application.models import Application
from backend.settings.env import ENV
from backend.utils.llm import get_llm_tokens
from backend.utils.viewset import BaseUndeletedModelViewSet

from .core.agents.charts_agent import ChartsAgent
from .core.agents.main_agent import DisplayFormat, EStepStatus, MainAgent
from .filters import MessageFilter
from .models import Message
from .serializers import MessageDetailSerializer, MessageSerializer


def get_cancelled_answer():
    return {
        "chart_option": "",
        "summary": "The chat has been cancelled.",
    }


def get_cancelled_response(message: Message):
    return {
        "id": message.id,
        "question": message.question,
        "answer": get_cancelled_answer(),
        "created_at": message.created_at,
        "completed_at": message.completed_at,
        "task_id": message.task_id,
        "is_cancelled": message.is_cancelled,
    }


async def get_application(user):
    return await Application.objects.aget(id=user.app_id)


async def get_last_message(user):
    return await Message.objects.filter(user=user).order_by("created_at").alast()


async def create_message(
    application_id,
    user,
    question,
    task_id,
):
    return await Message.objects.acreate(
        application_id=application_id,
        user=user,
        question=question,
        received_sql_list=[],
        valid_sql="",
        answer={"chart_option": "", "summary": ""},
        task_id=task_id,
    )


def get_error_response(message, status_code):
    return Response({"error": message}, status=status_code)


async def sse_chat_stream(generator):
    """
    Wrap the generator to provide Server-Sent Events (SSE).
    """
    async for step_data in generator:
        yield step_data


@api_view(http_method_names=["POST"])
async def chat_stream(request):
    """
    Chat with DB API through SSE (Server-Sent Events).
    """
    question = request.data.get("question")
    application_id = request.data.get("application_id")
    task_id = request.data.get("task_id")

    if not question:
        return get_error_response("Question is required", status.HTTP_400_BAD_REQUEST)

    if not application_id:
        return get_error_response(
            "Application id is required", status.HTTP_400_BAD_REQUEST
        )

    application = await Application.objects.aget(id=application_id)
    database_configuration = application.database_configuration

    if not database_configuration:
        return get_error_response(
            "Application is not configured properly", status.HTTP_400_BAD_REQUEST
        )

    context_history_question_count = int(ENV.CONTEXT_HISTORY_QUESTION_COUNT or 3)

    recent_messages = await sync_to_async(
        lambda: list(
            Message.objects.filter(
                user=request.user,
                application_id=application_id,
                is_deleted=False,
            ).order_by("-created_at")[:context_history_question_count]
        ),
        thread_sensitive=True,
    )()

    context = []
    context.append(
        f"User's historical questions are: <{[msg.optimized_question or msg.question for msg in recent_messages][::-1]}>"
    )

    context_question = "\n".join(context + [f"User's current question: {question}"])
    message = await create_message(
        application_id,
        request.user,
        question,
        task_id,
    )
    main_agent = MainAgent(application=application)

    async def generator():
        """
        Wrapper function to generate the responses step by step.
        """
        _steps = []
        optimized_question = question
        try:
            async for steps in main_agent.run_stream(context_question):
                _steps = steps
                for step in _steps:
                    step["id"] = str(message.id)
                    step["taskId"] = task_id
                    if step["step"] == "question_agent":
                        optimized_question = step["result"].get("new_question", "")
                res_data = camelize(_steps)
                if res_data[-1].get("queryResult"):
                    res_data[-1]["queryResult"] = []
                _message = await Message.objects.aget(id=message.id)
                if _message.is_cancelled:
                    res_data[-1]["status"] = EStepStatus.CANCELLED.value
                    yield f"data: {json.dumps(res_data)}\n\n"
                    return
                yield f"data: {json.dumps(res_data)}\n\n"

        except Exception as exc:
            latest_step = _steps[-1]
            latest_step["status"] = EStepStatus.ERROR.value
            latest_step["is_final_completed"] = True
            latest_step["answer"] = {
                "chart_option": "",
                "summary": "Sorry, No suitable results found.",
                "display_mode": DisplayFormat.TEXT.value,
            }
            latest_step["error_msg"] = str(exc)
            yield f"data: {json.dumps(camelize(_steps))}\n\n"

        finally:
            _message = await Message.objects.aget(id=message.id)
            if _message.is_cancelled:
                return
            # Record message completion at the end
            latest_step = _steps[-1]
            answer = latest_step.get("answer", {})
            answer["chart_option"] = ""
            message.answer = answer
            message.received_sql_list = latest_step.get("sql_list", [])
            message.valid_sql = latest_step.get("valid_sql", "")
            message.completed_at = datetime.now()
            message.query_result = latest_step.get("query_result", [])
            message.step_times = latest_step.get("step_times", {})
            message.optimized_question = optimized_question
            await message.asave()

    response = StreamingHttpResponse(
        generator(),
        content_type="text/event-stream",
    )
    return response


@api_view(http_method_names=["POST"])
async def generate_chart(request):
    message_id = request.data.get("message_id")
    language = request.data.get("language")
    message = await Message.objects.aget(id=message_id)
    charts_agent = ChartsAgent()
    query_result = message.query_result or []

    query_result_str = json.dumps(
        query_result, ensure_ascii=False, separators=(",", ":")
    )
    tokens = get_llm_tokens(query_result_str)

    if tokens > 32 * 1024 and len(query_result) > 0:
        query_result = query_result[: min(20, len(query_result))]
        query_result_str = json.dumps(
            query_result, ensure_ascii=False, separators=(",", ":")
        )

    user_question = f"**User question**: {message.optimized_question or message.question}\n **The language for generating charts is**: {language}"
    option_string = await sync_to_async(charts_agent.run)(
        user_question=user_question,
        query_result=query_result_str,
    )
    answer = message.answer or {}
    if option_string:
        answer["chart_option"] = option_string
        message.answer = answer
        await message.asave()
    return Response(
        {
            "id": message.id,
            "answer": answer,
            "created_at": message.created_at,
            "completed_at": message.completed_at,
            "task_id": message.task_id,
            "is_cancelled": message.is_cancelled,
        },
        status=status.HTTP_200_OK,
    )


@api_view(http_method_names=["POST"])
async def cancel_chat(request):
    task_id = request.data.get("task_id")
    message = await Message.objects.filter(
        user=request.user,
        task_id=task_id,
    ).afirst()
    if message:
        message.is_cancelled = True
        message.received_sql_list = []
        message.valid_sql = ""
        message.answer = get_cancelled_answer()
        message.completed_at = datetime.now()
        await message.asave()
    return Response(
        get_cancelled_response(message),
        status=status.HTTP_200_OK,
    )


class MessageViewSet(BaseUndeletedModelViewSet):
    """
    Message view set
    """

    queryset = Message.objects.filter(is_deleted=False).order_by("created_at")
    serializer_class = MessageSerializer
    filterset_class = MessageFilter
    ordering_fields = ["created_at"]

    def retrieve(self, request, *args, **kwargs):
        self.serializer_class = MessageDetailSerializer
        return super().retrieve(request, *args, **kwargs)

    @action(methods=["POST"], detail=False)
    def batch_delete(self, request, *args, **kwargs):
        ids = request.data.get("ids")
        if not ids:
            return Response(
                {"error": "IDs are required"}, status=status.HTTP_400_BAD_REQUEST
            )

        with transaction.atomic():
            messages = Message.objects.filter(id__in=ids, user=request.user)
            if not messages.exists():
                return Response(
                    {"error": "No messages found for the provided IDs"},
                    status=status.HTTP_404_NOT_FOUND,
                )
            messages.update(is_deleted=True)
        return Response({"success": True}, status=status.HTTP_200_OK)
