from tools.Models import Model
from tools.schema import Column , SerialPrimaryKey ,ForeignKey ,Varchar ,Boolean ,Integer

from dataclasses import dataclass, field ,asdict
from typing import List, Optional ,Dict ,Any
from functools import lru_cache
import logging

# Setup logging for debugging and error handling
logging.basicConfig(level=logging.INFO)

@dataclass
class Reviews(Model):
    id: SerialPrimaryKey = field(default_factory=SerialPrimaryKey)
    book_title: Varchar = field(
        default_factory=lambda: Varchar(length=200, not_null=True))
    rating: Integer = field(default_factory=lambda: Integer(check='rating >= 1 AND rating <= 5'))
    book_id: Optional[int] = None

    @classmethod
    def from_db(cls, row):
        return cls(
            id=row[5],  # Review ID
            rating=row[2],  # Rating
            book_title=row[3],  # Book title
            book_id=row[4],  # Book ID
        )
    
    def _convert_value(self, value):
        if isinstance(value, list):
            return [self._convert_value(item) for item in value]
        elif hasattr(value, 'to_dict'):
            return value.to_dict()
        else:
            return value

    def to_dict(self):
        return {k: self._convert_value(v) for k, v in self.__dict__.items()}

    def __str__(self):
        return f"Review: {self.book_title} - Rating: {self.rating}"


# Define the models using dataclasses
@dataclass
class User(Model):
    id: SerialPrimaryKey = field(default_factory=SerialPrimaryKey)
    username: Varchar = field(default_factory=lambda: Varchar(length=100, unique=True, not_null=True))
    password: Varchar = field(default_factory=lambda: Varchar(length=100, not_null=True))

    
    @classmethod
    @lru_cache(maxsize=128)
    def get_reviews(cls, user_id:int)-> Optional[Dict[str, Any]]:
        query = """
            SELECT
                u.id, u.username, r.rating, b.title AS book_title , r.book_id , r.id
            FROM
                users u
            LEFT JOIN
                reviews r ON u.id = r.user_id
            LEFT JOIN
                books b ON r.book_id = b.id
            WHERE
                u.id = %s
                    """
        try:
            results = cls._execute_query(query, (user_id,))

            if not results:
                return None

            user_info = {
                'id': results[0][0],
                'username': results[0][1],
                'reviews': []
            }

            for row in results:
                if row[2] is not None and row[3] is not None:
                    review:object = Reviews.from_db(row)
          
                    user_info['reviews'].append(review.to_dict())
            

            return user_info
        except Exception as e:
            logging.error(f"Error fetching user with reviews: {e}")
            return None
         











