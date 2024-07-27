from pathlib import Path
from typing import Optional, Union
from .DatabaseConncetor import PsqlConnector

class ContextFileManger:
    def __init__(self, path: Path):
        self.path = path

    def _handle_io(self, mode: str, content: Optional[str] = None) -> Union[str, bool, None]:
        try:
            with self.path.open(mode) as f:
                match mode:
                    case 'r':
                        return f.read()
                    case 'r+':
                        f.write(content or '')
                        f.seek(0)
                    case 'w' | 'a':
                        f.write(content or '')
            return True
        except FileNotFoundError:
            print(f"File '{self.path}' not found.")
        except IOError as e:
            print(f"IO Error: {e}")
        return None

    def read(self) -> Optional[str]:
        return self._handle_io('r')

    def write(self, content: str) -> None:
        if self._handle_io('w', content):
            print(f"File '{self.path}' written successfully.")

    def edit(self, new_content: str) -> None:
        if self._handle_io('r+', new_content):
            print(f"File '{self.path}' edited successfully.")

    def append(self, content: str) -> None:
        if self._handle_io('a', content):
            print(f"Content appended to file '{self.path}' successfully.")

    def delete(self) -> None:
        try:
            self.path.unlink()
            print(f"File '{self.path}' deleted successfully.")
        except FileNotFoundError:
            print(f"File '{self.path}' not found.")
        except IOError as e:
            print(f"Error deleting file: {e}")

    def execute_query(self) -> None:
        queries = self.read()
        if queries:
            with PsqlConnector() as cursor:
                for query in (q.strip() for q in queries.split(';') if q.strip()):
                    try:
                        cursor.execute(query)
                        print(f"Executed query: {query}")
                    except Exception as e:
                        print(f"Error executing query: {query}\n{e}")

    def __str__(self) -> str:
        return f"FileManager for file '{self.path}'"