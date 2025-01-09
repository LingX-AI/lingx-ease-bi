import json

from backend.apps.chat.core.utils import validate_json_string
from backend.settings.env import ENV
from backend.utils.llm import ChatCompletionService, get_llm_tokens

from ..prompts.column_comment_prompt import prompt as column_comment_prompt


class Agent:
    """
    Column comment agent
    """

    def __init__(self):
        self.current_execution_count = 1
        self.maximum_execution_count = 3

    def run(
        self,
        schema: str,
        database_description: str,
        tables: list[str],
        prompt: str,
    ) -> str:
        if self.current_execution_count > self.maximum_execution_count:
            raise Exception("Maximum execution count reached")
        _prompt = prompt or column_comment_prompt
        llm_messages = ChatCompletionService.set_llm_messages(
            system_content=_prompt.format(
                application_description=database_description,
                database_tables=json.dumps(tables),
            ),
            user_content=schema,
        )
        tokens = get_llm_tokens(llm_messages)
        result = ChatCompletionService.create_completion(
            model=f"ollama:{ENV.COLUMN_COMMENT_AGENT_MODEL}",
            messages=llm_messages,
            options={
                "num_ctx": tokens + 1024 * 4,  # Adjust num_ctx based on actual needs
                "num_batch": 512,
                "temperature": 0.5,
                "format": "json",
            },
        )
        result, _ = validate_json_string(result)
        if not result:
            self.current_execution_count += 1
            return self.run(schema, database_description, tables, prompt)
        return result
