import json

import sqlparse
from regex import P

from backend.apps.application.core.agents import schema_rag_agent
from backend.apps.application.models import (
    Application,
    ApplicationPrompt,
    FineTuningExample,
    FineTuningModel,
)
from backend.apps.application.utils import json_list_to_ddl
from backend.apps.chat.core.prompts.sql_generator_prompt import (
    prompt as sql_generator_prompt,
)
from backend.settings.env import ENV
from backend.utils.llm import (
    ChatCompletionService,
    LLMResponseFormat,
    create_application_schema,
    get_llm_tokens,
)


class SQLGeneratorAgent:
    def __init__(
        self,
        application: Application,
    ):
        self.schema = ""
        self.application = application
        self.current_execution_count = 1
        self.maximum_execution_count = 3
        application_prompt_instance = ApplicationPrompt.objects.filter(
            application=self.application
        ).first()
        if application_prompt_instance:
            self.sql_generator_prompt = (
                application_prompt_instance.sql_generator_prompt or sql_generator_prompt
            )
        else:
            self.sql_generator_prompt = sql_generator_prompt

    @staticmethod
    def verify_sql_syntax(sql: str) -> bool:
        """
        Verify if SQL syntax is correct
        :param sql:
        :return:
        """
        try:
            parsed = sqlparse.parse(sql)
            for statement in parsed:
                str(statement)
            return True
        except Exception as e:
            return False

    def get_schema(self, question: str):
        schema, _ = create_application_schema(application_id=self.application.id)
        agent_configuration = self.application.agent_configuration
        if not agent_configuration.get("rag_enabled"):
            # if RAG is not enabled, use the full schema from the application
            _, self.schema = json_list_to_ddl(schema)
            return
        else:
            agent = schema_rag_agent.Agent(application_id=self.application.id)
            recalled_tables = json.loads(agent.run(question))
        tables = []
        for item in schema:
            if item["table"] in recalled_tables:
                tables.append(item)
        _, self.schema = json_list_to_ddl(tables)

    def run(self, question: str):
        if self.current_execution_count > self.maximum_execution_count:
            raise Exception("Maximum execution count reached")
        if not self.schema:
            self.get_schema(question)

        fine_tuning_examples = FineTuningExample.objects.filter(
            application=self.application,
            is_enabled=True,
        ).order_by("created_at")

        llm_messages = ChatCompletionService.set_llm_messages(
            system_content=self.sql_generator_prompt.format(
                db=self.application.database_configuration.get("db"),
                database_schema=self.schema,
            ),
            user_content=question,
        )

        if fine_tuning_examples:
            examples_context = []
            for example in fine_tuning_examples:
                examples_context.extend(
                    [
                        {
                            "role": "user",
                            "content": example.question,
                        },
                        {
                            "role": "assistant",
                            "content": example.sql,
                        },
                    ]
                )
            llm_messages[1:1] = examples_context

        _model = FineTuningModel.objects.filter(
            application=self.application, is_enabled=True
        ).first()
        model_name = _model.model_name if _model else ENV.SQL_GENERATOR_AGENT_MODEL
        tokens = get_llm_tokens(llm_messages)
        result = ChatCompletionService.create_completion(
            model=f"ollama:{model_name}",
            messages=llm_messages,
            options={
                "num_ctx": tokens + 1024,
                "num_batch": 512,
                "temperature": 0,
            },
        )
        if not result:
            self.current_execution_count += 1
            return self.run(question)
        return LLMResponseFormat.extract_sql_str(result)
