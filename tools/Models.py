from .DatabaseConncetor import PsqlConnector
from schema import *
from typing import List, Type, Dict, Any, Optional
from functools import lru_cache
import logging

# Setup logging for debugging and error handling
logging.basicConfig(level=logging.INFO)


class ModelMeta(type):
    def __new__(cls, name, bases, dct):
        if name != 'Model':
            columns = {k: v for k, v in dct.items()}
            dct['_columns'] = columns
            dct['table_name'] = name.lower() + 's'

            # Add the create method to the class
            def create(cls, **kwargs):
                # Create a new instance without calling __init__
                instance = cls.__new__(cls)
                for key, value in kwargs.items():
                    setattr(instance, key, value)
                return instance

            dct['create'] = classmethod(create)

        return super().__new__(cls, name, bases, dct)


class Model(metaclass=ModelMeta):

    @classmethod
    def _execute_query(cls, query: str, params: Optional[tuple] = ()) -> List[tuple]:
        try:
            with PsqlConnector.get_cursor() as cursor:
                cursor.execute(query, params)
                return cursor.fetchall()
        except Exception as e:
            logging.error(f"Error executing query: {e}")
            return []

    @classmethod
    def _fetch_as_dicts(cls, query: str, params: tuple, keys: List[tuple]) -> List[Dict[str, Any]]:
        """Executes a query and returns the result as a list of dictionaries."""
        rows = cls._execute_query(query, params)
        return [{key: value for key, value in zip(keys, row)} for row in rows]

    @classmethod
    @lru_cache(maxsize=128)
    def get_columns(cls) -> List[str]:
        query = "SELECT column_name FROM information_schema.columns WHERE table_name = %s;"
        params = (cls.table_name,)
        columns = cls._execute_query(query, params)
        return [row[0] for row in columns]

    @classmethod
    @lru_cache(maxsize=128)
    def get(cls, **kwargs) -> list[dict]:
        columns = cls.get_columns()
        condition = ' AND '.join([f"{k} = %s" for k in kwargs])
        values = tuple(kwargs.values())
        query = f'SELECT * FROM {cls.table_name} WHERE {condition};'
        return cls._fetch_as_dicts(query, values, columns)

    @classmethod
    def insert(cls, **kwargs):
        columns = ', '.join(kwargs.keys())
        values = ', '.join(['%s'] * len(kwargs))
        query = f'INSERT INTO {cls.table_name} ({columns}) VALUES ({values}) RETURNING id;'
        params = tuple(kwargs.values())
        raw_id = cls._execute_query(query, params)[0][0]
        row_dict = cls.get(id=raw_id)
        return row_dict

    @classmethod
    def create_table(cls):
        columns_definitions = ', '.join(
            f"{name} {col}" for name, col in cls._columns.items())
        foreign_keys = [f"FOREIGN KEY ({name}) {col}" for name, col in cls._columns.items() if isinstance(col, ForeignKey)]
        unique_constraints = [name for name, col in cls._columns.items(
        ) if col.unique and not isinstance(col, ForeignKey)]
        check_constraints = [
            f"CHECK ({col.check})" for name, col in cls._columns.items() if col.check]

        query_parts = [columns_definitions] + foreign_keys
        if unique_constraints:
            query_parts.append(f"UNIQUE ({', '.join(unique_constraints)})")
        query_parts.extend(check_constraints)

        query = f'CREATE TABLE IF NOT EXISTS {
            cls.table_name} ({", ".join(query_parts)});'
        cls._execute_query(query)

    @classmethod
    def drop_table(cls):
        query = f'DROP TABLE IF EXISTS {cls.table_name};'
        cls._execute_query(query)

    @classmethod
    def all(cls, filter: Optional[Dict[str, Any]] = None) -> List[dict]:
        columns = cls.get_columns()
        query = f'SELECT * FROM {cls.table_name}'
        params = ()
        if filter:
            condition = ' AND '.join([f"{k} = %s" for k in filter.keys()])
            query += f' WHERE {condition}'
            params = tuple(filter.values())

        return cls._fetch_as_dicts(query, params, columns)

    @classmethod
    def update(cls, id, **kwargs) -> None:

        updates = ', '.join([f"{k} = %s" for k in kwargs])
        values = tuple(kwargs.values()) + (id,)
        query = f"UPDATE {cls.table_name} SET {updates} WHERE id = %s;"
        cls._execute_query(query, values)
        # for k, v in kwargs.items():
        #     setattr( k, v)

    @classmethod
    def destroy(cls, instance):
        query = f'DELETE FROM {cls.table_name} WHERE id = %s;'
        params = (instance.id,)
        instance._execute_query(query, params)
