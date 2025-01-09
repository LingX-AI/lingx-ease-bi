import json
from urllib.parse import quote

import pandas as pd
import sqlalchemy
from sqlalchemy.exc import SQLAlchemyError


class DatabaseQueryAgent:
    """
    Database Query Agent
    """

    def __init__(self, database_configuration: dict):
        db_user = database_configuration.get("db_user")
        db_password = quote(str(database_configuration.get("db_password", "")))
        db_host = database_configuration.get("db_host")
        db_port = database_configuration.get("db_port")
        db_name = database_configuration.get("db_name")
        database_uri = f"mysql+mysqlconnector://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
        self.user_question: str = ""
        self.sql_list: list[str] = []
        self.error_msgs: list[str] = []
        self.engine = sqlalchemy.create_engine(database_uri)

    @staticmethod
    def _sql_error_handler(e) -> str:
        """
        Catch execution errors
        """
        try:
            return str(getattr(e, "orig", e))
        except Exception as _e:
            return str(_e)

    def _generate_execute_prompt(self) -> str:
        """
        if has error, generate execute prompt
        :return:
        """
        sql_error_prompt = f"User question:{self.user_question}\n"
        for index, sql in enumerate(self.sql_list):
            sql_error_prompt += f"- Error SQL {index + 1}: {sql}\n- The SQL that encountered an error: {self.error_msgs[index]}\n"
        sql_error_prompt += "Please analyze the above SQL and the reasons for the execution error, and regenerate a new correct SQL."
        return sql_error_prompt

    def run(self, _user_question, sql_list):
        self.user_question = _user_question
        self.sql_list = sql_list
        self.error_msgs = []
        for sql_query in sql_list:
            try:
                df = pd.read_sql_query(sql_query, self.engine)
                query_result = df.to_json(orient="records", force_ascii=False)
                return json.dumps(json.loads(query_result), ensure_ascii=False, separators=(',', ':')), sql_query, self.error_msgs
            except Exception as e:
                error_msg = self._sql_error_handler(e)
                self.error_msgs.append(error_msg)
        return None, None, self._generate_execute_prompt()
