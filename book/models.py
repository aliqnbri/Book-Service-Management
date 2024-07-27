from tools.Models import Model
from tools.schema import Varchar, SerialPrimaryKey
from dataclasses import dataclass, field, asdict
from typing import List, Optional, Dict, Any
from django.urls import reverse
from functools import lru_cache
import logging


# Setup logging for debugging and error handling
logging.basicConfig(level=logging.INFO)


@dataclass
class Reviews:
    rating: Optional[int]
    username: Optional[str]
 



@dataclass
class Books(Model):
    id: SerialPrimaryKey = field(default_factory=SerialPrimaryKey)
    title: Varchar = field(
        default_factory=lambda: Varchar(length=200, not_null=True))
    author: Varchar = field(
        default_factory=lambda: Varchar(length=200, not_null=True))
    genre: Varchar = field(
        default_factory=lambda: Varchar(length=100, not_null=True))
    reviews: List[Reviews] = field(default_factory=list)

    def _convert_value(self, value):
        if isinstance(value, list):
            return [self._convert_value(item) for item in value]
        elif hasattr(value, 'to_dict'):
            return value.to_dict()
        else:
            return value

    def to_dict(self):
        return {k: self._convert_value(v) for k, v in self.__dict__.items()}

    def get_absolute_url(self) -> str:
        return reverse('book-detail', kwargs={'id': self.id})

    @classmethod
    @lru_cache(maxsize=128)
    def get_book_with_reviews(cls, book_id: int) -> Optional[Dict[str, Any]]:
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
            b.id = %s
        """

        try:
            results = cls._execute_query(query, (book_id,))
            if not results:
                return None

            book_info = {
                'id': results[0][0],
                'title': results[0][1],
                'author': results[0][2],
                'genre': results[0][3],
                'reviews': []
            }

            for row in results:
                if row[4] is not None and row[5] is not None:
                    review = Reviews(rating=row[4], username=row[5])
                    book_info['reviews'].append(asdict(review))

            return book_info

        except Exception as e:
            logging.error(f"Error fetching book with reviews: {e}")
            return None

    # @classmethod
    # @lru_cache(maxsize=128)
    # def get_all_book_ids(cls) -> List[int]:
    #     query = "SELECT id FROM books"

    #     try:
    #         results = cls._execute_query(query)
    #         return [row['id'] for row in results]

    #     except Exception as e:

    #         logging.error(f"Error fetching all book ids: {e}")
    #         return []
