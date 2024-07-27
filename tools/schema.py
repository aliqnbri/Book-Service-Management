class Table:
    def __init__(self, name, *columns):
        self.name = name
        self.columns = columns

    def create_table_query(self):
        query = f"CREATE TABLE {self.name} ("
        column_queries = [str(column) for column in self.columns]
        query += ", ".join(column_queries)
        query += ");"
        return query    



class Column:
    def __init__(self, data_type=True, primary_key=False,unique=True, check=None, not_null=True, **kwargs):
        self.data_type = data_type
        self.primary_key = primary_key
        self.unique = unique
        self.not_null = not_null
        self.check = check
        self.kwargs = kwargs

    def __str__(self):
        query = self.data_type
        if self.primary_key:
            query += " PRIMARY KEY"
        if self.unique:
            query += " UNIQUE"
        if self.not_null ==True:
            query += " NOT NULL"
        else:
            query += "NULL"    
        if self.check:
            query += f" CHECK({self.check})"    
        if self.kwargs:
            query += " " + " ".join(f"{k} {v}" for k, v in self.kwargs.items())
        return query

class ForeignKey:
    def __init__(self, table,on_delete=None, **kwargs):
        self.table = table
        self.on_delete = on_delete
        self.kwargs = kwargs

    def __str__(self):
        query = f"REFERENCES {self.table}"
        if self.on_delete:
            query += f" ON DELETE {self.on_delete}"
        if self.kwargs:
            query += " " + " ".join(f"{k} {v}" for k, v in self.kwargs.items())
        return query

class Integer(Column):
    def __init__(self, **kwargs):
        super().__init__("INTEGER", **kwargs)

class SerialPrimaryKey(Column):
    def __init__(self, **kwargs):
        self.primary_key = True
        self.unique = True
        self.not_null = False
        super().__init__("SERIAL PRIMARY KEY", **kwargs)

class Varchar(Column):
    def __init__(self, length, **kwargs):
        super().__init__(f"VARCHAR({length})", **kwargs)

class Boolean(Column):
    def __init__(self, default=False, **kwargs):
        super().__init__(f"BOOLEAN DEFAULT {default}", **kwargs)