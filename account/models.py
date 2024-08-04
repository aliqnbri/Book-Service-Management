from tools.Models import Model
from book.models import Review
from typing import List, Dict, Optional ,Any

import logging

# Setup logging for debugging and error handling
logging.basicConfig(level=logging.INFO)
from book.models import Book

from collections import defaultdict    




class User(Model):

    @classmethod
    def identify_favorite_genre(cls,user_reviews: List[Dict[str, Any]]) -> str:

        genre_count = defaultdict(int)
        for review in user_reviews:
            print(review)
            book_id = review['book_id']
            book = Book.get(id=book_id)[0]
            genre = book['genre']
            genre_count[genre] += 1
        max_genre = max(genre_count, key=genre_count.get)    
        return {'genre': max_genre}



    @classmethod
    def recommend_books(cls, user_id: int, top_n: int = 5) -> List[Dict[str, Any]]:
        if not (user_reviews := cls.get_reviews(user_id)) or  None:
            return "There is not enough data about you."
        
        favorite_genre = cls.identify_favorite_genre(user_reviews)
        recommended_books = Book.all(filter=favorite_genre)

        return recommended_books[:top_n]
        



    @classmethod
    def all_users(cls, filter: Optional[Dict[str, Any]] = None, ordering: Optional[List[str]] = None) -> List[dict]:
        query = f'SELECT * FROM {cls.table_name}'
        params = ()
        if filter:
            condition = ' AND '.join([f"{k} = %s" for k in filter.keys()])
            query += f' WHERE {condition}'
            params = tuple(filter.values())

        if ordering:
            ordering_clause = ', '.join(ordering)
            query += f' ORDER BY {ordering_clause}'    

        return cls._fetch_as_dicts(query, params, keys=['id', 'username'])
    
    # @lru_cache(maxsize=128)
    @classmethod
    def get_user(cls, **kwargs) -> list[dict]:
        columns = cls.get_columns()
        condition = ' AND '.join([f"{k} = %s" for k in kwargs])
        values = tuple(kwargs.values())
        query = f'SELECT * FROM {cls.table_name} WHERE {condition};'
        return cls._fetch_as_dicts(query, values, columns)

    @classmethod
    def get_user_info(cls,user_id) -> List[Dict[str, Any]]:
        query = """
            SELECT 
                id, username
            FROM 
                users
            WHERE id = %s;
        """
        params = (user_id,)
        return cls._fetch_as_dicts(query,params, keys=['id', 'username'])

    @classmethod
    def get_reviews(cls, user_id:int=None)-> List[Dict[str, any]]:
        query = """
            SELECT 
                    r.id, b.id, b.title, r.rating
            FROM 
                users u
            JOIN 
                reviews r ON u.id = r.user_id
            JOIN 
                books b ON r.book_id = b.id
            WHERE 
                u.id = %s;
            """
        params = (user_id,)
        result = cls._execute_query(query, params)

        return [
            {
                'review_id': row[0],
                'book_id': row[1],
                'book_title': row[2],
                'rating': row[3],
            }
            for row in result
        ]


    @classmethod
    def get_by_reviews(cls, user_id:int)-> Optional[Dict[str, any]]:
        reviews = cls.get_reviews(user_id=user_id)
        user_data =  dict(*tuple(cls.get_user_info(user_id=user_id)))
        if user_data:
            user_data['reviews'] = reviews
        return user_data

    











