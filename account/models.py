from tools.Models import Model
from book.models import Review
from typing import List, Dict, Optional

import logging

# Setup logging for debugging and error handling
logging.basicConfig(level=logging.INFO)




class User(Model):
    pass
    @classmethod
    def get_reviews(cls, user_id:int=None)-> List[Dict[str, any]]:
        query = """
            SELECT 
                    b.id, b.title, r.rating
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
                'book_id': row[0],
                'book_title': row[1],
                'rating': row[2],
            }
            for row in result
        ]


    @classmethod
    def get_by_reviews(cls, user_id:int)-> Optional[Dict[str, any]]:
        reviews = cls.get_reviews(user_id=user_id)
        user_data =  dict(*tuple(User.get(id=2)))
        if user_data:
            user_data['reviews'] = reviews
        return user_data

    











