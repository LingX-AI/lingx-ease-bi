import json
from enum import Enum
from re import L

import requests

from backend.apps.chat.core.prompts.answer_generator_prompt import (
    prompt as answer_generator_prompt,
)
from backend.apps.chat.core.utils import validate_json_string
from backend.settings.env import ENV
from backend.utils.llm import ChatCompletionService, get_llm_tokens


class AnswerGeneratorAgent:
    """
    Answer Generator Agent
    """

    def __init__(self):
        self.maximum_execution_count: int = 3
        self.current_execution_count: int = 1

    async def run(
        self,
        user_question: str,
        query_result: str,
    ):
        model_name = ENV.ANSWER_GENERATOR_AGENT_MODEL
        tokens = get_llm_tokens(query_result)
        query_result = json.loads(query_result)
        total_count = len(query_result)
        note = f"Note: Found {total_count} records in total."
        if tokens > 32 * 1024:
            max_result_count = 0
            total_tokens = 0
            for row in query_result:
                row_tokens = get_llm_tokens(json.dumps(row))
                if total_tokens + row_tokens > 32 * 1024:
                    break
                total_tokens += row_tokens
                max_result_count += 1
            query_result = query_result[:max_result_count]
            note = f"Note: Found {total_count} records in total, only showing partial records due to context length limitations"
        llm_messages = ChatCompletionService.set_llm_messages(
            system_content=answer_generator_prompt,
            user_content=f"Question: {user_question}\nQuery results: `{query_result}`\n{note}",
        )
        tokens = get_llm_tokens(llm_messages)
        for chunk in ChatCompletionService.create_stream_completion(
            model=f"ollama:{model_name}",
            messages=llm_messages,
            options={
                "num_ctx": tokens * 2,
                "num_batch": 512,
                "temperature": 0,
            },
        ):
            yield chunk
