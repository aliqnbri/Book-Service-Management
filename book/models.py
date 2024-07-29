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
    def get_reviews(cls, book_id):
        query = """
            SELECT 
                u.username, r.rating
            FROM 
                reviews r
            JOIN 
                users u ON r.user_id = u.id
            JOIN 
                books b ON r.book_id = b.id
            WHERE 
                b.id = %s;

        """
        params = (book_id,)
        result = cls._execute_query(query, params)

        return [{
            'user': row[0],
            'rating': row[1],
        } for row in result]
    
    @classmethod
    def get_book_by_reviews(cls, book_id:int):
        reviews = cls.get_reviews(book_id=book_id)
        book_data= dict(*tuple(cls.get(id=book_id)))
        if book_data:
            book_data['reviews'] = reviews
        return book_data        
    

    



