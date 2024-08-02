from rest_framework import serializers
from tools import HashPassword
from rest_framework.response import Response
from rest_framework import status

from django.urls import reverse
from tools.CustomAuthentication import authenticate
from .models import User
from typing import Dict , Any , List


class BaseSerializer(serializers.Serializer):
    """Base serializer to handle common methods and attributes."""

    def get_detail_url(self, obj: Dict[str, Any], view_name, lookup_field='id'):
        request = self.context.get('request')
        lookup_value = obj.get(lookup_field)
        return request.build_absolute_uri(reverse(view_name, args=[lookup_value]))


class UserSerializer(BaseSerializer):
    id = serializers.IntegerField()
    username = serializers.CharField()

    def get_reviews(self, instance: Dict) -> List[Dict[str, Any]]:
        return instance.get('reviews', [])
    

    def get_recommends(self, instance):
        request = self.context.get('request')
        return request.build_absolute_uri(reverse('account:user-suggest', args=[instance['id']]))
    
    def get_review_representations(self, instance: Dict[str, Any]) -> List[Dict[str, Any]]:
        reviews = self.get_reviews(instance)
        return [
            {
                'book ID': review['book_id'],
                'book Detail': self.get_detail_url({'id': review['book_id']}, 'book:book-detail', 'id'),
                'book Title': review['book_title'],
                'rating': review['rating']
            } for review in reviews
        ]

    def to_representation(self, instance: Dict[str, Any]) -> Dict[str, Any]:
        representation = super().to_representation(instance)
        view = self.context.get('view')

        if view is not None:
            match view.action:
                case 'list' | 'destroy':
                    representation['user_detail'] = self.get_detail_url(instance , 'account:user-detail', 'id')
                case 'retrieve' | 'create'| 'suggest':
                    representation.pop('user_detail',None)
                    representation['recommends'] = self.get_recommends(instance)
                    representation['reviews'] = self.get_review_representations(instance)      
        return representation


class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=100)
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    password2 = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'}, label="Confirm Password")

    def validate(self, data: str) -> str:
        # Custom validation method to check if the username already exists
        if data['password'] != data['password2']:
            raise serializers.ValidationError("Password fields didn't match.")

        if User.get(username = data['username']):
            raise serializers.ValidationError(f"User {data} already exists")
        data.pop('password2')
        return data

    def create(self, validated_data: dict) -> list[Dict]:
        username = validated_data['username']
        password = validated_data['password']

        # Hash the password and insert the user
        hashed_password = HashPassword.hash_password(password)
        instance = User.insert(username=username, password=hashed_password)
        return instance


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
