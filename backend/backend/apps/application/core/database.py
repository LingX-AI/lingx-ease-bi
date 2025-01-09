import urllib.parse

import pandas as pd
import sqlalchemy


class DatabaseExecutor:
    def __init__(self, database_configuration: dict):
        self.db_user = database_configuration.get("db_user")
        self.db_password = urllib.parse.quote(database_configuration.get("db_password"), "")
        self.db_host = database_configuration.get("db_host")
        self.db_port = database_configuration.get("db_port")
        self.db_name = database_configuration.get("db_name")
        self.database_uri = (
            f"mysql+mysqlconnector://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"
        )
        print(self.database_uri)
        self.engine = sqlalchemy.create_engine(self.database_uri)

    def execute(self, sql_query: str) -> pd.DataFrame:
        df = pd.read_sql_query(sql_query, self.engine)
        return df

    def get_ddl(self):
        """
        Get DDL
        :return:
        """
        df = self.execute("SHOW TABLES")
        ddl_list = []
        for item in df.to_numpy():
            table_name = item[0]
            _df = self.execute(f"SHOW CREATE TABLE {table_name}")
            table_ddl = _df.to_numpy()[0][1]
            ddl_list.append(table_ddl)
        return ddl_list

    def create_tables(self):
        """
        Get DDL JSON
        :return:
        """
        df = self.execute(
            f"""
                SELECT TABLE_NAME, TABLE_COMMENT
                FROM INFORMATION_SCHEMA.TABLES
                WHERE TABLE_SCHEMA = '{self.db_name}';
"""
        )
        tables = [
            {
                "table_name": row[0],
                "comment": row[1],
            }
            for row in df.to_numpy()
        ]
        ddl_json = []
        for item in tables:
            table_name = item["table_name"]
            query = f"""
                        SELECT COLUMN_NAME, COLUMN_TYPE, IS_NULLABLE, COLUMN_KEY, COLUMN_DEFAULT, COLUMN_COMMENT
                        FROM INFORMATION_SCHEMA.COLUMNS
                        WHERE TABLE_SCHEMA = '{self.db_name}' AND TABLE_NAME = '{table_name}';
                    """
            df = self.execute(query)
            table_ddl = {
                "table_name": table_name,
                "comment": item["comment"],
                "columns": [
                    {
                        "name": row[0],
                        "type": row[1],
                        "nullable": row[2],
                        "key": row[3],
                        "default": row[4],
                        "comment": row[5],
                    }
                    for row in df.to_numpy()
                ],
            }
            ddl_json.append(table_ddl)
        return ddl_json
