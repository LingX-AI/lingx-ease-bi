import json
import math

from backend.apps.application.models import Application
from backend.apps.application.utils import json_list_to_ddl
from backend.apps.chat.core.utils import validate_json_string
from backend.settings.env import ENV
from backend.utils.llm import (
    ChatCompletionService,
    create_application_schema,
    get_llm_tokens,
)

from ..prompts.schema_rag_prompt import prompt as schema_rag_prompt


class Agent:
    """
    DB schema rag agent
    """

    def __init__(self, application_id):
        self.schema_ddl_str = ""
        self.current_execution_count = 1
        self.maximum_execution_count = 3
        self.application_id = application_id
        self.schema_rag_prompt = Application.objects.get(
            id=application_id
        ).prompts.schema_rag_prompt
        self.schema_rag_prompt = self.schema_rag_prompt or schema_rag_prompt
        schema, self.schema_str = create_application_schema(application_id)
        _, self.schema_ddl_str = json_list_to_ddl(schema)

    def run(
        self,
        question: str,
    ) -> str:
        if self.current_execution_count > self.maximum_execution_count:
            raise Exception("Maximum execution count reached")
        llm_messages = ChatCompletionService.set_llm_messages(
            system_content=self.schema_rag_prompt.format(
                database_schema=self.schema_ddl_str,
            ),
            user_content=question,
        )
        tokens = get_llm_tokens(llm_messages)
        result = ChatCompletionService.create_completion(
            model=f"ollama:{ENV.SCHEMA_RAG_MODEL}",
            messages=llm_messages,
            options={
                "num_ctx": tokens + 512,
                "num_batch": 512,
                "temperature": 0.3,
            },
        )
        result, _ = validate_json_string(result)
        if not result:
            self.current_execution_count += 1
            return self.run(question)
        return result
