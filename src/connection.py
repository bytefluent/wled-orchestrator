from functools import lru_cache
import json

import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.sql import text

from loguru import logger

class DBConnection(object):
    db_file = 'storage.db'

    def __init__(self, endpoint=None, default_table=None, primary_key=None):
        self.default_table = default_table
        self.primary_key = primary_key
        self.endpoint = endpoint or f"sqlite:///{self.db_file}"
        self.conflict = ""

    __instance = None

    @classmethod
    def instance(cls):
        if not cls.__instance:
            cls.__instance = DBConnection()
        return cls.__instance

    @lru_cache(1)
    def engine(self):
        return create_engine(self.endpoint)

    def prep(self, v):
        if isinstance(v, dict):
            return json.dumps(v)
        if isinstance(v, list):
            return json.dumps(v)
        return v

    def clear(self, table):
        q = text(f"DELETE FROM {table}")
        with self.engine().connect() as _connection:
            _connection.execute(q)

    def insert(self, objects):
        if type(objects) == dict:
            objects = [objects]

        columns = objects[0].keys()
        clist = ", ".join([f'"{c}"' for c in columns])
        plist = ", ".join([':' + c for c in columns])

        returning = '' # f" RETURNING {self.primary_key}" if self.primary_key else ""

        insert_query = text(f"INSERT INTO {self.default_table}({clist}) VALUES({plist}){self.conflict}{returning}")
        # logger.debug(insert_query)
        results = []
        with self.engine().connect() as _connection:
            for obj in objects:
                prepped = { k: self.prep(v) for k, v in obj.items()}
                logger.debug(prepped)
                if returning:
                    for row in _connection.execute(insert_query, **prepped):
                        results.append(row)
                else:
                    try:
                        results.append(_connection.execute(insert_query, **prepped).inserted_primary_key)
                    except:
                        pass
        return results

    def _resolve(self, v):
        if 'Decimal' in str(type(v)):
            return float(v)
        return v

    def _results(self, results):
        return [dict(zip(r.keys(), [self._resolve(v) for v in r.values()])) for r in results]

    def select_all(self, table=None):
        table = table or self.default_table
        with self.engine().connect() as _connection:
            return self._results(
                _connection.execute(text(f'SELECT * from {table}')))

    def query(self, sql):
        with self.engine().connect() as _connection:
            _connection.execute(text(sql))
