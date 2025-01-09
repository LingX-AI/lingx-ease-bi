import json
from typing import Iterator

from backend.apps.application.models import Application
from backend.apps.chat.core.prompts.question_prompt import prompt as question_prompt
from backend.apps.chat.core.utils import validate_json_string
from backend.settings.env import ENV
from backend.utils.llm import ChatCompletionService, get_llm_tokens


class QuestionAgent:
    """
    Question Agent
    """

    def __init__(self, application: Application):
        self.application = application
        self.current_execution_count = 1
        self.maximum_execution_count = 3
        self.compliant_value = 0.6

    def judge_question_compliant(self, result: str) -> tuple[bool, str, str]:
        """
        Judge if the question is compliant
        :param result:
        :return:
        """
        compliant_dict = json.loads(result)
        value = compliant_dict.get("compliant", 0)
        return (
            value >= self.compliant_value,
            compliant_dict.get("new_question", ""),
            compliant_dict.get("language", "英文"),
        )

    def run(
        self,
        user_question: str,
    ) -> tuple[bool, str, str]:
        if self.current_execution_count > self.maximum_execution_count:
            return False, "", ""
        tables = [
            {
                "name": item.name,
                "comment": item.ai_comment or item.comment,
            }
            for item in self.application.tables.filter(
                is_deleted=False,
                is_enabled=True,
            )
        ]
        llm_messages = ChatCompletionService.set_llm_messages(
            system_content=question_prompt.format(
                application_name=self.application.name,
                application_description=self.application.description,
                database_tables=tables,
            ),
            user_content=f"User question: {user_question}",
        )
        tokens = get_llm_tokens(llm_messages)
        result = ChatCompletionService.create_completion(
            model=f"ollama:{ENV.QUESTION_AGENT_MODEL}",
            messages=llm_messages,
            options={
                "num_ctx": tokens + 1024,
                "num_batch": 512,
                "temperature": 0.4,
            },
            format="json",
        )
        result, _ = validate_json_string(result)
        if not result:
            self.current_execution_count += 1
            return self.run(user_question)
        return self.judge_question_compliant(result)
