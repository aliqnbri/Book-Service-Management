from tools.DatabaseConncetor import PsqlConnector
from tools import HashPassword
from rest_framework import status
from rest_framework.response import Response


def authenticate(username: str, password: str, table_name='users') -> bool:
    """Authenticate a user by comparing the provided password with the stored hash in PostgreSQL."""


    query = f"SELECT password FROM {table_name} WHERE username = %s;"
    
    try:
        with PsqlConnector() as cursor:
            cursor.execute(query, (username,))
            row = cursor.fetchone()
    except Exception:
        return Response({"error": "Internal Server Error while authenticating User."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    if row is None:
        return False  # Username not found
    print(row)

    stored_hash = row[0]
    return HashPassword.hash_password(password) == stored_hash