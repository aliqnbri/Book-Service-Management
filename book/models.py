from tools.Models import Model
from typing import List, Optional, Dict, Any
from functools import lru_cache



class Review(Model):
    pass


class Book(Model):
    @classmethod
    @lru_cache(maxsize=128)
    def get_all_id(cls) -> List[int]:
        results = cls.all()
        return [row['id'] for row in results]



    @classmethod
    def _construct_book_info(cls, results) -> Dict[str, Any]:
        book_info = {
            'id': results[0][0],
            'title': results[0][1],
            'author': results[0][2],
            'genre': results[0][3],
            'reviews': [{'rating': row[4], 'user': row[5]} for row in results if row[4] is not None and row[5] is not None]
          
        }
        return book_info

    @classmethod
    @lru_cache(maxsize=128)
    def get_book_by_reviews(cls, book_id: int) -> Optional[Dict[str, Any]]:
        query = """
        SELECT
            b.id, b.title, b.author, b.genre, r.rating, u.username
        FROM
            books b
        LEFT JOIN
            reviews r ON b.id = r.book_id
        LEFT JOIN
            users u ON r.user_id = u.id
        WHERE
            b.id = %s;
        """
        params = (book_id,)
        results = tuple(cls._execute_query(query,params))
        if not results:
            return None

        book_info = {
            'id': results[0][0],
            'title': results[0][1],
            'author': results[0][2],
            'genre': results[0][3],
            'reviews': [{'rating': row[4], 'user': row[5]} for row in results if row[4] is not None and row[5] is not None]
          
        }
        return book_info
    



