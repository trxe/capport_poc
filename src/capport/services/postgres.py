from typing import Mapping

import psycopg

from tools.logger import Logger


class PostgresResponse:
    def __init__(self, cmd: str, res: any = None):
        self.cmd = cmd
        self.res = res

    def __str__(self):
        return f"CMD:\n{self.cmd}\n\nRES: {self.res}"


class PostgreSQLDB:
    @classmethod
    def create_table(cls, table_name: str, varlist: list[list[str]], noop: bool = True):
        fields = ",\n".join([" ".join(x) for x in varlist])
        cmd = f"CREATE TABLE IF NOT EXISTS {table_name} ({fields});"
        return PostgresResponse(cmd=cmd, res=None if noop else cls.conn.execute(cmd))

    @classmethod
    def _insert_cmd(
        cls, table_name: str, datamap: Mapping[str, any], conflict_keys: list[str]
    ):
        data = list(datamap.items())
        keys = [x[0] for x in data]
        placeholders = ", ".join(["%s"] * len(keys))
        keystr = ", ".join(keys)
        cmd = f"""INSERT INTO {table_name} ({keystr}) 
                VALUES ({placeholders})
                ON CONFLICT ({', '.join(conflict_keys)}) DO NOTHING
                RETURNING {keystr};"""
        return cmd

    @classmethod
    def insert_many(
        cls,
        table_name: str,
        datamaplist: list[Mapping[str, any]],
        conflict_keys: list[str],
    ):
        if not datamaplist:
            return None
        cmd = cls._insert_cmd(table_name, datamaplist[0], conflict_keys)
        values = list(tuple(datamap.values()) for datamap in datamaplist)
        print(cmd)
        print(values[0])
        # print(values)
        with cls.conn.cursor() as cur:
            cur.executemany(cmd, values)

    @classmethod
    def insert(
        cls, table_name: str, datamap: Mapping[str, any], conflict_keys: list[str]
    ):
        cmd = cls._insert_cmd(cls, table_name, datamap, conflict_keys)
        values = tuple(datamap.values())
        return cls.conn.execute(cmd, values)

    @classmethod
    def select(cls, table_name: str, keylist: list[str], additional: str):
        cmd = f"SELECT {', '.join(keylist)} FROM {table_name} {additional};"
        return cls.conn.execute(cmd)

    @classmethod
    def create_enum(cls, typename, enum_values):
        enum_str = "', '".join(enum_values)
        cmd = f"""
DO $$ BEGIN
    CREATE TYPE {typename} AS ('{enum_str}');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;
        """
        return cls.conn.execute(cmd)

    @classmethod
    def execute(cls, cmd):
        return cls.conn.execute(cmd)

    @classmethod
    def commit(cls):
        cls.conn.commit()

    @classmethod
    def start(cls, host, port, dbname, user=None, password=None):
        # Service name is required for most backends
        cls.conn = psycopg.connect(
            user=user, password=password, host=host, port=port, dbname=dbname
        )
        cursor = cls.conn.cursor()
        Logger.info("Connection successful.")

        # Example query
        cursor.execute("SELECT NOW();")
        result = cursor.fetchone()
        Logger.info("Current Time:", result)

    @classmethod
    def end(cls):
        if cls.conn:
            cls.conn.close()
            Logger.info("Connection closed.")
