from rest_framework.authentication import BaseAuthentication
from account.models import User
from rest_framework.exceptions import AuthenticationFailed
from django.conf import settings
import datetime
import jwt
from rest_framework_simplejwt.tokens import RefreshToken
from tools.DatabaseConncetor import PsqlConnector
from tools import HashPassword
from rest_framework import status
from rest_framework.response import Response
from typing import Optional


def authenticate(username: str, password: str, table_name='users') -> bool:
    """Authenticate a user by comparing the provided password with the stored hash in PostgreSQL."""

    query = f"SELECT password FROM {table_name} WHERE username = %s;"

    params = (username, )

    try:
        with PsqlConnector.get_cursor() as cursor:
            cursor.execute(query, params)
            row = cursor.fetchone()
    except Exception as e:
        return Response({"error": "Internal Server Error while authenticating User."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    if row is None:
        return False  # Username not found
    stored_hash = row[0]
    return HashPassword.hash_password(password) == stored_hash


class JWTService:
    secret_key = settings.SECRET_KEY
    algorithm = 'HS256'

    @classmethod
    def token_generator(cls, user: dict, expiry_minutes: int = 60) -> str:
        payload = {
            'user_id': user['id'],
            'username': user['username'],
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=expiry_minutes),
            'iat': datetime.datetime.utcnow()
        }
        token = jwt.encode(payload, cls.secret_key, cls.algorithm)
        return token

    @classmethod
    def refresh_token_generator(self, user: dict, expiry_days: int = 7) -> str:
        """
        Generates a refresh token for a user.
        """
        payload = {
            'user_id': user['id'],
            'username': user['username'],
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=expiry_days),
            'iat': datetime.datetime.utcnow()
        }
        refresh_token = jwt.encode(
            payload, self.secret_key, algorithm=self.algorithm)
        return refresh_token

    @classmethod
    def new_token_generator(cls, refresh_token: str) -> Optional[str]:
        """
        Generates a new access token if the provided refresh token is valid.
        """
        if not (payload := cls.is_token_valid(refresh_token)):
            return None

        user = {
            'id': payload['user_id'],
            'username': payload['username']
        }
        new_access_token = cls.token_generator(user)
        return new_access_token

    @classmethod
    def is_token_valid(cls, token: str) -> Optional[dict]:
        try:
            payload = jwt.decode(token, cls.secret_key,
                                 algorithms=[cls.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            # Token has expired
            return None
        except jwt.InvalidTokenError:
            # Token is invalid or corrupted
            return None
        except jwt.DecodeError:
            # Token cannot be decoded
            return None


class JWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        if not (token := request.COOKIES.get('jwt')):
            return None
        if (payload := JWTService.is_token_valid(token)):
            user = User.get(id=payload['user_id'])[0]
            return (user, None)
        raise AuthenticationFailed('User not found')
