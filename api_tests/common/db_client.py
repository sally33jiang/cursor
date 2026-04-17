from typing import Iterable, List

import pymysql


class DbClient:
    def __init__(self, db_config: dict):
        self.db_config = db_config
        self.conn = None

    def connect(self) -> None:
        self.conn = pymysql.connect(
            host=self.db_config["host"],
            port=int(self.db_config.get("port", 3306)),
            user=self.db_config["user"],
            password=self.db_config["password"],
            database=self.db_config["database"],
            charset=self.db_config.get("charset", "utf8mb4"),
            autocommit=True,
        )

    def close(self) -> None:
        if self.conn:
            self.conn.close()
            self.conn = None

    def execute_many(self, sql_list: Iterable[str]) -> List[int]:
        if not self.conn:
            self.connect()
        results = []
        with self.conn.cursor() as cursor:
            for sql in sql_list:
                results.append(cursor.execute(sql))
        return results
