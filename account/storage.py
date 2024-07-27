import logging
from typing import List, Dict, Any, Optional
from contextlib import contextmanager
from tools.DatabaseConncetor import PsqlConnector



class Storage:
    
    @classmethod
    def _execute_query(cls, query: str, params: Optional[tuple] = ()) -> List[tuple]:
        """Executes a SQL query and returns the results."""
        try:
            with PsqlConnector.get_cursor() as cursor:
                cursor.execute(query, params)
                return cursor.fetchall()
        except Exception as e:
            logging.error(f"Error executing query: {e}")
            return []

    @staticmethod
    def _fetch_as_dicts(query: str ,params, keys) -> List[Dict[str, Any]]:
        """Executes a query and returns the result as a list of dictionaries."""
        rows = Storage._execute_query(query, params)
        return [dict(zip(keys, row)) for row in rows]
    
    def get_reviews(self) -> List[Dict[str, Any]]:
        query = "SELECT user_id, book_id, rating FROM reviews;"
        return self._fetch_as_dicts(query, keys=['user_id', 'book_id', 'rating'])
    
    def get_user_reviews(self, user_id: int) -> List[Dict[str, Any]]:
        query = "SELECT book_id, rating FROM reviews WHERE user_id = %s;"
        params = (user_id,)
        return self._fetch_as_dicts(query, params, keys=['book_id', 'rating'])
    
    def get_book(self, book_id: int) -> Dict[str, Any]:
        query = "SELECT id, title, genre, author FROM books WHERE id = %s;"
        params = (book_id,)
        rows = self._fetch_as_dicts(query, params, keys=['id', 'title', 'genre', 'author'])
        return rows[0] if rows else {}
    
    def get_books_by_genre(self, genre: str) -> List[Dict[str, Any]]:
        query = "SELECT id, title, genre, author FROM books WHERE genre = %s;"
        params = (genre,)
        return self._fetch_as_dicts(query, params, keys=['id', 'title', 'genre', 'author', 'average_rating'])

