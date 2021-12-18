
import os
import time
import json
import sqlite3

from sqlalchemy import text, Table, Column, Integer, String, MetaData
from sqlalchemy.sql.sqltypes import Boolean

from connection import DBConnection

def initialize():
    if os.path.exists(DBConnection.db_file):
        return
        
    meta = MetaData()

    SettingsTable.schema(meta)
    LEDsTable.schema(meta)
    PatternTable.schema(meta)
    ScheduleTable.schema(meta)
    LEDsGroupTable.schema(meta)

    meta.create_all(DBConnection.instance().engine())

class SettingsTable(DBConnection):

    def __init__(self):
        DBConnection.__init__(self, default_table='settings', primary_key='id')
        self.conflict = " ON CONFLICT(key) DO UPDATE SET value=excluded.value"

    @classmethod
    def schema(cls, meta):
        Table('settings', meta, 
            Column('id', Integer, primary_key = True), 
            Column('key', String, unique = True), 
            Column('value', String), 
        )

    def __setitem__(self, key, value):
        self.insert(dict(key=key, value=json.dumps(value)))

    def __getitem__(self, key):
        with self.engine().connect() as _connection:
            results = self._results(
                _connection.execute(
                    text(f'''
                        SELECT *
                        FROM {self.default_table}
                        WHERE key = :k
                    '''), k=key))
            return json.loads(results[0]['value']) if results else None

    def get(self, key, default=None):
        return self[key] or default

    def all_as_dict(self):
        return {r['key']: json.loads(r['value']) for r in self.select_all()}


class ScheduleTable(DBConnection):

    def __init__(self):
        DBConnection.__init__(self, default_table='schedule', primary_key='id')
        self.conflict = ''' ON CONFLICT(id) DO UPDATE SET 
            name=excluded.name, 
            start_time=excluded.start_time, 
            end_time=excluded.end_time,
            string_json=excluded.string_json, 
            effects_json=excluded.effects_json,
            enabled=excluded.enabled'''

    @classmethod
    def schema(cls, meta):
        Table('schedule', meta, 
            Column('id', Integer, primary_key = True), 
            Column('name', String), 
            Column('start_time', Integer), 
            Column('end_time', Integer), 
            Column('string_json', String), 
            Column('effects_json', String), 
            Column('enabled', Boolean), 
        )

    def save(self, schedule):
        schedule['string_json'] = json.dumps(schedule['string_json'])
        schedule['effects_json'] = json.dumps(schedule['effects_json'])
        self.insert(schedule)

    def get_all(self):
        schedules = self.select_all()
        for schedule in schedules:
            schedule['string_json'] = json.loads(schedule['string_json'])
            schedule['effects_json'] = json.loads(schedule['effects_json'])
        return schedules


class LEDsTable(DBConnection):

    def __init__(self):
        DBConnection.__init__(self, default_table='leds', primary_key='id')


    @classmethod
    def schema(cls, meta):
        Table('leds', meta, 
            Column('id', Integer, primary_key = True), 
            Column('name', String), 
            Column('addr', String), 
            Column('ip_addr', String), 
            Column('first_time', Integer), 
            Column('last_time', Integer),
            Column('current_pattern', Integer)
        )

    def by_id(self, id):
        with self.engine().connect() as _connection:
            return self._results(
                _connection.execute(
                    text(f'''
                        SELECT *
                        FROM {self.default_table}
                        WHERE {self.primary_key} = {id}
                    ''')))

    def by_name(self, name):
        with self.engine().connect() as _connection:
            results = self._results(
                _connection.execute(
                    text(f'''
                        SELECT *
                        FROM {self.default_table}
                        WHERE name = :n
                    '''), n=name))
            return results[0] if results else None

    def update_pattern(self, name, pattern_id):
        with self.engine().connect() as _connection:
            _connection.execute(
                    text(f'''
                        UPDATE {self.default_table}
                        SET current_pattern = :p, last_time = :t
                        WHERE name = :n
                    '''), p=pattern_id, n=name, t=time.time())


class PatternTable(DBConnection):

    def __init__(self):
        DBConnection.__init__(self, default_table='pattern', primary_key='id')
        self.conflict = ''' ON CONFLICT(id) DO UPDATE SET 
            name=excluded.name, 
            color1=excluded.color1, 
            color2=excluded.color2, 
            color3=excluded.color3, 
            effect=excluded.effect, 
            palette=excluded.palette,
            intensity=excluded.intensity, 
            speed=excluded.speed'''

    @classmethod
    def schema(cls, meta):
        Table('pattern', meta, 
            Column('id', Integer, primary_key = True), 
            Column('name', String), 
            Column('color1', String), 
            Column('color2', String), 
            Column('color3', String), 
            Column('effect', Integer), 
            Column('palette', Integer), 
            Column('intensity', Integer), 
            Column('speed', Integer), 
        )

    def by_id(self, id):
        with self.engine().connect() as _connection:
            results = self._results(
                _connection.execute(
                    text(f'''
                        SELECT *
                        FROM {self.default_table}
                        WHERE {self.primary_key} = {id}
                    ''')))
            result = results[0] if results else None
            if result:
                result['color1'] = json.loads(result['color1'])
                result['color2'] = json.loads(result['color2'])
                result['color3'] = json.loads(result['color3'])

            return result

    def save(self, pattern):
        result = self.insert(pattern)
        return self.by_id(result[0]) if result else pattern

class LEDsGroupTable(DBConnection):

    def __init__(self):
        DBConnection.__init__(self, default_table='leds_group', primary_key='id')
        self.conflict = ''' ON CONFLICT(id) DO UPDATE SET 
            name=excluded.name, 
            group_json=excluded.group_json'''

    @classmethod
    def schema(cls, meta):
        Table('leds_group', meta, 
            Column('id', Integer, primary_key = True), 
            Column('name', String), 
            Column('group_json', String), 
        )

    def save(self, group):
        group['group_json'] = json.dumps(group['group_json'])
        self.insert(group)

    def get_all(self):
        groups = self.select_all()
        for group in groups:
            group['group_json'] = json.loads(group['group_json'])
        return groups


if __name__ == '__main__':
    initialize()