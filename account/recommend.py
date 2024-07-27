from .storage import Storage
from typing import List, Dict, Any, Optional

def identify_favorite_genre(user_reviews: List[Dict[str, Any]], storage: Storage) -> str:
    genre_count = {}
    
    for review in user_reviews:
        book_id = review['book_id']
        book = storage.get_book(book_id)
        genre = book['genre']
        
        if genre in genre_count:
            genre_count[genre] += 1
        else:
            genre_count[genre] = 1
    
    return max(genre_count, key=genre_count.get)

def recommend_books(user_id: int, storage: Storage, top_n: int = 5) -> List[Dict[str, Any]]:
    user_reviews = storage.get_user_reviews(user_id)
    
    if len(user_reviews) < 1:
        return "There is not enough data about you."
    
    favorite_genre = identify_favorite_genre(user_reviews, storage)
    books_in_favorite_genre = storage.get_books_by_genre(favorite_genre)
    
    user_reviewed_books = {review['book_id'] for review in user_reviews}
    recommended_books = [book for book in books_in_favorite_genre if book['id'] not in user_reviewed_books]

    
    return recommended_books[:top_n]
