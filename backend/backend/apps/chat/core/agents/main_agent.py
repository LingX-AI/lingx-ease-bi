import json
import time
from enum import Enum

from asgiref.sync import sync_to_async
from regex import P

from backend.apps.application.models import Application

from .answer_generator_agent import AnswerGeneratorAgent
from .database_query_agent import DatabaseQueryAgent
from .question_agent import QuestionAgent
from .sql_generator_agent import SQLGeneratorAgent


class DisplayFormat(Enum):
    CHART = "chart"
    TABLE = "table"
    TEXT = "text"


class EStepStatus(Enum):
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ERROR = "error"
    CANCELLED = "cancelled"


class MainAgent:
    def __init__(
        self,
        application: Application,
        maximum_execution_count: int = 3,
        current_execution_count: int = 1,
    ):
        self.maximum_execution_count = maximum_execution_count
        self.current_execution_count = current_execution_count
        self.application = application
        self.database_configuration = application.database_configuration
        self.user_question = ""
        self.step_times = {}
        self.timestamp = None
        self.steps = []

    def _set_step_time(self, step_name: str = ""):
        if step_name:
            old_time = self.step_times.get("step_name", float(0))
            current_time = time.time()
            if self.timestamp:
                self.step_times[step_name] = old_time + round(
                    current_time - self.timestamp, 2
                )
                return round(current_time - self.timestamp, 2)
        self.timestamp = time.time()
        return 0

    async def run_stream(self, user_question: str, error_prompt: str = ""):
        """
        :param user_question: User question for database
        :param error_prompt: Error prompt for database
        :yield: answer, sql_list, valid_sql, query_result, step_times
        """
        question_agent = QuestionAgent(application=self.application)
        sql_generator_agent = await sync_to_async(SQLGeneratorAgent)(
            application=self.application
        )
        db_query_agent = DatabaseQueryAgent(
            database_configuration=self.database_configuration
        )

        # Step 1: QuestionAgent - Process user question
        self.steps.append(
            {
                "step": "question_agent",
                "status": EStepStatus.IN_PROGRESS.value,
                "result": {"is_compliant": None},
                "latency": 0,
            }
        )
        yield self.steps

        self._set_step_time()

        # Run question_agent asynchronously
        is_compliant, new_question, language = await sync_to_async(question_agent.run)(
            user_question
        )
        latency = self._set_step_time("question_agent")

        # Update question-agent step result
        self.steps[-1]["status"] = EStepStatus.COMPLETED.value
        self.steps[-1]["result"] = {
            "is_compliant": is_compliant,
            "new_question": new_question,
            "language": language,
        }
        self.steps[-1]["latency"] = latency
        yield self.steps

        # If not compliant, respond with error message and terminate the processing
        if not is_compliant:
            answer = {
                "summary": "Sorry, your question is not relevant to the current system. Please try another one...",
                "chart_option": "",
                "display_mode": DisplayFormat.TEXT.value,
            }
            self.steps.append(
                {
                    "step": "answer_generator_agent",
                    "status": EStepStatus.COMPLETED.value,
                    "result": answer,
                    "is_final_completed": True,
                    "answer": answer,
                    "sql_list": [],
                    "valid_sql": "",
                    "query_result": [],
                    "step_times": self.step_times,
                    "latency": 0,
                }
            )
            yield self.steps
            return

        # Step 2: SQLGeneratorAgent - Generate SQL
        self.steps.append(
            {
                "step": "sql_generator_agent",
                "status": EStepStatus.IN_PROGRESS.value,
                "result": [],
                "latency": 0,
            }
        )
        yield self.steps

        self._set_step_time()

        # Run sql_generator_agent to generate SQL statements
        sql = await sync_to_async(sql_generator_agent.run)(
            error_prompt or new_question,
        )
        sql_list = [sql]
        latency = self._set_step_time("sql_generator_agent")

        # Update sql_generator_agent step result
        self.steps[-1]["status"] = EStepStatus.COMPLETED.value
        self.steps[-1]["result"] = sql_list
        self.steps[-1]["latency"] = latency
        yield self.steps

        # Step 3: DatabaseQueryAgent - Execute SQL on database
        self.steps.append(
            {
                "step": "db_query_agent",
                "status": EStepStatus.IN_PROGRESS.value,
                "result": [],
                "latency": 0,
            }
        )
        yield self.steps

        self._set_step_time()

        # Query the database based on the generated SQL list
        query_result, valid_sql, _error_prompt = await sync_to_async(
            db_query_agent.run
        )(new_question, sql_list)
        latency = self._set_step_time("db_query_agent")

        # Check for empty query_result
        if query_result is None:
            self.current_execution_count += 1
            self.steps[-1]["status"] = EStepStatus.ERROR.value
            self.steps[-1]["result"] = _error_prompt
            # Handle retries if query result is empty
            if self.current_execution_count <= self.maximum_execution_count:
                error_msg = (
                    _error_prompt
                    if isinstance(_error_prompt, str)
                    else str(_error_prompt)
                )
                async for step in self.run_stream(
                    user_question=new_question, error_prompt=error_msg
                ):
                    yield step
                return
            else:
                # Final response if maximum retries have been exceeded
                self.steps.append(
                    {
                        "step": "answer_generator_agent",
                        "status": EStepStatus.COMPLETED.value,
                        "answer": {
                            "summary": "Sorry, no suitable results found.",
                            "chart_option": "",
                            "display_mode": DisplayFormat.TEXT.value,
                        },
                        "is_final_completed": True,
                        "result": {},
                        "sql_list": [],
                        "valid_sql": "",
                        "query_result": [],
                        "step_times": self.step_times,
                        "latency": latency,
                    }
                )
                yield self.steps
                return

        # Update db_query_agent step result
        self.steps[-1]["status"] = EStepStatus.COMPLETED.value
        self.steps[-1]["result"] = []
        self.steps[-1]["latency"] = latency
        yield self.steps

        # Step 4: AnswerGeneratorAgent - Generate natural language answer
        self.steps.append(
            {
                "step": "answer_generator_agent",
                "status": EStepStatus.IN_PROGRESS.value,
                "result": {
                    "summary": "",
                    "display_mode": DisplayFormat.TEXT.value,
                },
                "latency": 0,
            }
        )
        yield self.steps

        self._set_step_time()

        answer_generator = AnswerGeneratorAgent()
        answer_text = ""
        async for chunk in answer_generator.run(
            user_question=f"Please answer the question in {language}: {new_question}",
            query_result=query_result,
        ):
            answer_text += chunk
            if "<chart></chart>" in answer_text:
                answer_text = answer_text.replace("<chart></chart>", "")
                self.steps[-1]["result"]["display_mode"] = DisplayFormat.CHART.value
            if "<data-table></data-table>" in answer_text:
                answer_text = answer_text.replace("<data-table></data-table>", "")
                self.steps[-1]["result"]["display_mode"] = DisplayFormat.TABLE.value
            self.steps[-1]["result"]["summary"] = answer_text
            yield self.steps

        latency = self._set_step_time("answer_generator_agent")

        self.steps[-1]["status"] = EStepStatus.COMPLETED.value
        self.steps[-1]["answer"] = self.steps[-1]["result"]
        self.steps[-1]["latency"] = latency
        self.steps[-1]["is_final_completed"] = True
        self.steps[-1]["sql_list"] = sql_list
        self.steps[-1]["valid_sql"] = valid_sql
        self.steps[-1]["query_result"] = json.loads(query_result, strict=False)
        self.steps[-1]["step_times"] = self.step_times
        yield self.steps
        return
