from backend.apps.chat.core.prompts.charts_prompt import prompt as charts_prompt
from backend.apps.chat.core.utils import validate_json_string
from backend.settings.env import ENV
from backend.utils.llm import ChatCompletionService, get_llm_tokens


class ChartsAgent:
    """
    Charts Agent
    """

    def __init__(self):
        self.user_question = None
        self.query_result = None
        self.echarts_maximum_execution_count: int = 3
        self.echarts_current_execution_count: int = 1

    def run(
        self,
        user_question: str,
        query_result: str,
        _charts_prompt: str = charts_prompt,
    ) -> str:
        if self.echarts_current_execution_count > self.echarts_maximum_execution_count:
            return ""
        self.user_question = user_question
        self.query_result = query_result
        llm_messages = ChatCompletionService.set_llm_messages(
            system_content=_charts_prompt,
            user_content=f"User Question: {self.user_question}\nQuery Data: {self.query_result}",
        )
        tokens = get_llm_tokens(llm_messages)
        result = ChatCompletionService.create_completion(
            model=f"ollama:{ENV.CHARTS_AGENT_MODEL}",
            messages=llm_messages,
            options={
                "num_ctx": tokens * 2,
                "num_batch": 512,
                "temperature": 0,
            },
            format="json",
        )
        return result
