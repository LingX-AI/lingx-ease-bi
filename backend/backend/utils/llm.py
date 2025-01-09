import json
import re
from typing import Generator, Iterator, Optional

import aisuite as ai
import tiktoken

from backend.apps.application.models import ApplicationTable

client = ai.Client()
client.configure(
    {
        "ollama": {
            "timeout": 600,
        }
    }
)


def get_llm_tokens(messages: str | list[dict]):
    encoding = tiktoken.encoding_for_model("gpt-4o")
    if isinstance(messages, list):
        text = json.dumps(messages, separators=(",", ":"), ensure_ascii=False)
    else:
        text = messages
    tokens = encoding.encode(text)
    return len(tokens)


class LLMResponseFormat:
    @classmethod
    def extract_sql_str(cls, res: str):
        if not res:
            return None
        if res.startswith("```sql"):
            return res.split("```sql")[1].split("```")[0].strip()
        return res.strip()

    @classmethod
    def _validate_json_string(
        cls, json_str: str
    ) -> tuple[Optional[str], Optional[str]]:
        """
        Helper method to validate JSON string
        """
        try:
            json.loads(json_str, strict=False)
            return json_str, None
        except json.JSONDecodeError:
            return None, "Not a valid JSON string"

    @classmethod
    def extract_json_str(cls, json_str: str) -> tuple[Optional[str], Optional[str]]:
        """
        Validate JSON string.
        :param json_str: JSON string to validate.
        :return: tuple (validated JSON string or None, error message or None)
        """
        error_msg = "Not a valid JSON string"

        if json_str:
            try:
                json.loads(json_str, strict=False)
                return json_str, None
            except json.JSONDecodeError:
                if json_str.startswith("```json") and json_str.endswith("```"):
                    match = re.match(r"```json(.*)```", json_str, re.DOTALL)
                    if match:
                        option_string = match.group(1).strip()
                        return cls._validate_json_string(option_string)

                elif json_str.startswith("```json"):
                    match = re.match(r"```json(.*)", json_str, re.DOTALL)
                    if match:
                        option_string = match.group(1).strip()
                        return cls._validate_json_string(option_string)

                elif json_str.endswith("```"):
                    match = re.match(r"(.*)```", json_str, re.DOTALL)
                    if match:
                        option_string = match.group(1).strip()
                        return cls._validate_json_string(option_string)

                return None, error_msg

        return None, error_msg


def create_application_schema(application_id) -> tuple[list[dict], str]:
    table_instances = ApplicationTable.objects.filter(
        application_id=application_id, is_enabled=True
    ).prefetch_related("columns")
    schema = [
        {
            "table": table.name,
            "comment": table.ai_comment,
            "columns": [
                {
                    "name": col.name,
                    "key": col.key,
                    "type": col.type,
                    "default": col.default,
                    "comment": col.ai_comment,
                    "nullable": col.nullable,
                }
                for col in table.columns.filter(is_enabled=True)  # type: ignore
            ],
        }
        for table in table_instances
    ]
    return schema, json.dumps(schema, separators=(",", ":"), ensure_ascii=False)


class ChatCompletionService:

    @staticmethod
    def set_llm_messages(
        system_content: str,
        user_content: str,
    ) -> list[dict[str, str]]:
        return [
            {
                "role": "system",
                "content": system_content,
            },
            {
                "role": "user",
                "content": user_content,
            },
        ]

    @staticmethod
    def create_completion(
        model: str,
        messages: list[dict[str, str]],
        **kwargs,
    ) -> str:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            **kwargs,
        )
        return response.choices[0].message.content

    @staticmethod
    def create_stream_completion(
        model: str,
        messages: list[dict[str, str]],
        **kwargs,
    ) -> Generator[str, None, None]:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            stream=True,
            **kwargs,
        )

        for chunk in response:
            if chunk.choices[0].delta.content is not None:
                yield chunk.choices[0].delta.content
