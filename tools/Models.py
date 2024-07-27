from .DatabaseConncetor import PsqlConnector
from .schema import Column, ForeignKey
from typing import List, Type, Dict, Any, Optional
import logging

# Setup logging for debugging and error handling
logging.basicConfig(level=logging.INFO)


class ModelMeta(type):
    def __new__(cls, name, bases, dct):
        if name != 'Model':
            columns = {k: v for k, v in dct.items(
            ) if isinstance(v, (Column, ForeignKey))}
            dct['_columns'] = columns
            dct['table_name'] = name.lower()

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
            with PsqlConnector() as psql:
                psql.execute(query, params)
                return psql.fetchall()
        except Exception as e:
            logging.error(f"Error executing query: {e}")
            return []

    @classmethod
    def get_columns(cls) -> List[str]:
        query = "SELECT column_name FROM information_schema.columns WHERE table_name = %s;"
        params = (cls.table_name,)
        columns = cls._execute_query(query, params)
        return [row[0] for row in columns]

    @classmethod
    def get_object(cls, **kwargs) -> Optional['Model']:
        columns = cls.get_columns()
        condition = ' AND '.join([f"{k} = %s" for k in kwargs])
        values = tuple(kwargs.values())
        query = f'SELECT * FROM {cls.table_name} WHERE {condition};'

        rows = cls._execute_query(query, values)
        if rows:
            return cls.create(**dict(zip(columns, rows[0])))
        return None

    @classmethod
    def insert(cls: Type['Model'], **kwargs) -> 'Model':
        columns = ', '.join(kwargs.keys())
        values = ', '.join(['%s'] * len(kwargs))
        query = f'INSERT INTO {cls.table_name} ({columns}) VALUES ({values}) RETURNING id;'
        params = tuple(kwargs.values())
        raw_id = cls._execute_query(query, params)[0][0]
        obj = cls.get_object(id=raw_id)
        return obj

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
    def all(cls, filter: Optional[Dict[str, Any]] = None) -> List['Model']:
        columns = cls.get_columns()
        query = f'SELECT * FROM {cls.table_name}'
        params = ()
        if filter:
            condition = ' AND '.join([f"{k} = %s" for k in filter.keys()])
            query += f' WHERE {condition}'
            params = tuple(filter.values())

        rows = cls._execute_query(query, params)
        return [cls.create(**dict(zip(columns, row))) for row in rows]

    def update(self,id, **kwargs):
        if id:
            id = self.id
        updates = ', '.join([f"{k} = %s" for k in kwargs])
        values = tuple(kwargs.values()) + (self.id,)
        query = f"UPDATE {self.table_name} SET {updates} WHERE id = %s;"
        self._execute_query(query, values)
        if id == self.id:
            for k, v in kwargs.items():
                setattr(self, k, v)

    # def delete(self):
    #     query = f'DELETE FROM {self.table_name} WHERE id = %s;'
    #     params = (self.id,)
    #     self._execute_query(query, params)


    @classmethod
    def destroy(cls, instance):
        query = f'DELETE FROM {cls.table_name} WHERE id = %s;'
        params = (instance.id,)
        instance._execute_query(query, params)    


   
    