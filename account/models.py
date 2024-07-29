from tools.Models import Model
from book.models import Review
from typing import List, Dict, Optional ,Any

import logging

# Setup logging for debugging and error handling
logging.basicConfig(level=logging.INFO)






class User(Model):


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
        return cls._fetch_as_dicts(query,params, keys=['id', 'usrname'])

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
        user_data =  dict(*tuple(cls.get_user_info(user_id=user_id)))
        if user_data:
            user_data['reviews'] = reviews
        return user_data

    











