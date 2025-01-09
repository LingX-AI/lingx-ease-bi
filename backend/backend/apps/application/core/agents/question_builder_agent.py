import json
import math

from backend.apps.application.models import Application, ApplicationPrompt
from backend.apps.chat.core.utils import validate_json_string
from backend.settings.env import ENV
from backend.utils.llm import (
    ChatCompletionService,
    create_application_schema,
    get_llm_tokens,
)

from ..prompts.question_builder_prompt import prompt as question_builder_prompt


class Agent:
    """
    Column comment agent
    """

    def __init__(self, application_id):
        self.schema_str = None
        self.current_execution_count = 1
        self.maximum_execution_count = 3
        self.application_id = application_id
        self.application = Application.objects.get(id=application_id)
        self.app_description = self.application.description
        application_prompt_instance = ApplicationPrompt.objects.filter(
            application_id=application_id
        ).first()
        if (
            application_prompt_instance
            and application_prompt_instance.question_builder_prompt
        ):
            self.question_builder_prompt = (
                application_prompt_instance.question_builder_prompt
            )
        else:
            self.question_builder_prompt = question_builder_prompt
        _, self.schema_str = create_application_schema(application_id)

    def run(
        self,
        question_count: int = 10,
    ) -> str:
        if self.current_execution_count > self.maximum_execution_count:
            raise Exception("Maximum execution count reached")
        llm_messages = ChatCompletionService.set_llm_messages(
            system_content=self.question_builder_prompt.format(
                application_description=self.app_description,
                database_schema=self.schema_str,
            ),
            user_content=f"Please generate {question_count} different questions as requested.",
        )
        tokens = get_llm_tokens(json.dumps(llm_messages))
        result = ChatCompletionService.create_completion(
            model=f"ollama:{ENV.QUESTION_BUILDER_MODEL}",
            messages=llm_messages,
            options={
                "num_ctx": tokens + 1024 * 2,
                "num_batch": 512,
                "temperature": 0.8,
            },
        )
        result, _ = validate_json_string(result)
        if not result:
            self.current_execution_count += 1
            return self.run(question_count)
        return result
