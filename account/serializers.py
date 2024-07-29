from rest_framework import serializers
from tools import HashPassword
from rest_framework.response import Response
from rest_framework import status
from tools.CustomAuthentication import authenticate
from django.urls import reverse
from tools.DatabaseConncetor import PsqlConnector
from .models import User
from typing import Dict , Any


class BaseSerializer(serializers.Serializer):
    """Base serializer to handle common methods and attributes."""

    def get_detail_url(self, obj, view_name, lookup_field='book_id'):
        request = self.context.get('request')
        lookup_value = obj.get(lookup_field)
        return request.build_absolute_uri(reverse(view_name, args=[lookup_value]))

    def fetch_book_title(self, book_id):
        query = 'SELECT title FROM books WHERE id = %s;'
        params = (book_id,)
        try:
            with PsqlConnector() as psql:
                psql.execute(query, params)
                result = psql.fetchone()
                return result[0] if result else 'Unknown'
        except Exception as e:
            print(f"Error fetching book title: {e}")
            return 'Unknown'





class UserSerializer(BaseSerializer):
    id = serializers.IntegerField()
    username = serializers.CharField()
    # book_list_url= serializers.SerializerMethodField()
    # reviews = serializers.ListField()
    # recommends = serializers.SerializerMethodField()



    # def get_book_list_url(self,instance):
    #     request = self.context.get('request')
    #     return request.build_absolute_uri(reverse('book:book-list'),kwargs={'id': instance['id']})


    # def get_recommends(self, instance):
    #     request = self.context.get('request')
    #     return request.build_absolute_uri(reverse('account:user-suggest', args=[instance['id']]))
    


    def to_representation(self, instance: User) -> Dict[str, Any]:
        representation = super().to_representation(instance)
        view = self.context.get('view')

        match view.action:
            case 'list' | 'destroy':
                representation['user_detail'] = self.get_detail_url(instance , 'account:user-detail', 'id')
        #         representation.pop('reviews', None)
        #         representation.pop('recommends', None)
        #     # case 'retrieve' | 'create':
        #     #     representation.pop('detail_url')
        #     #     representation = {
        #     #         'list_url': self.get_list_url(), **representation}
        #     #     representation['reviews'] = self.get_reviews(instance)
        #     # case 'update':
        #     #     representation['reviews'] = self.get_reviews(instance)

        return representation

    # def to_representation(self, instance):
    #     representation = super().to_representation(instance)
    #     reviews = instance.get('reviews', [])

    #     review_representations = [
    #         {
    #             'review_detail': self.get_detail_url(review, 'account:review-detail', 'id'),
    #             'book_detail_url': self.get_detail_url(review, 'book:book-detail'),
    #             'book_title': self.fetch_book_title(review['book_id']),
    #             'rating': review['rating'],
    #         }
    #         for review in reviews
    #     ]
    #     representation['reviews'] = review_representations
    #     representation['recommends'] = self.get_recommends(instance)

        

    #     return representation


class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=100)
    password = serializers.CharField(write_only=True, max_length=128)

    def validate_username(self, value: str) -> str:
        # Custom validation method to check if the username already exists
        if User.get_object(username=value):
            raise serializers.ValidationError(f"User {value} already exists")
        return value

    def create(self, validated_data: dict) -> object:
        username = validated_data['username']
        password = validated_data['password']

        # Hash the password and insert the user
        hashed_password = HashPassword.hash_password(password)
        obj = User.insert(username=username, password=hashed_password)
        return obj


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=100)
    password = serializers.CharField(write_only=True, max_length=128)

    def validate(self, data):
        username = data.get('username')
        password = data.get('password')

        if authenticate(username=username, password=password):
            return data
        raise serializers.ValidationError(
            {'error': 'Invalid credentials'})
