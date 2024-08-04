from functools import cached_property
from django.urls import reverse_lazy
from tools.CustomAuthentication import JWTService
from rest_framework import serializers
from tools import HashPassword
from rest_framework.response import Response
from rest_framework import status
from django.urls import reverse
from tools.CustomAuthentication import authenticate
from .models import User
from typing import Dict, Any, List


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

    def get_reviews_list(self, instance):
        request = self.context.get('request')
        return request.build_absolute_uri(reverse('account:reviews-list', kwargs={'user_id': instance['id']}))

    def get_recommends(self, instance):
        request = self.context.get('request')
        return request.build_absolute_uri(reverse('account:user-suggest', args=[instance['id']]))

    def to_representation(self, instance: Dict[str, Any]) -> Dict[str, Any]:
        representation = super().to_representation(instance)
        view = self.context.get('view')

        if view is not None:
            match view.action:
                case 'list' | 'destroy':
                    representation['user_detail'] = self.get_detail_url(
                        instance, 'account:user-detail', 'id')
                case 'retrieve' | 'create' | 'suggest':
                    representation.pop('user_detail', None)
                    representation['recommends'] = self.get_recommends(
                        instance)
                    representation['reviews'] = self.get_reviews_list(instance)

        return representation


class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=100)
    password = serializers.CharField(write_only=True, required=True, style={
                                     'input_type': 'password'})
    password2 = serializers.CharField(write_only=True, required=True, style={
                                      'input_type': 'password'}, label="Confirm Password")

    def validate(self, data: str) -> str:
        # Custom validation method to check if the username already exists
        if data['password'] != data['password2']:
            raise serializers.ValidationError("Password fields didn't match.")

        if User.get(username=data['username']):
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


class ReviewSerializer(BaseSerializer):
    id = serializers.IntegerField(read_only=True)
    user_id = serializers.CharField(read_only=True)
    book_id = serializers.IntegerField()
    rating = serializers.IntegerField(min_value=1, max_value=5)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.context.get('view').action == 'update':
            self.fields['book_id'].read_only = True

    @cached_property
    def get_user(self):
        request = self.context.get('request')
        refresh_token = request.COOKIES.get('refresh_token')
        token = request.COOKIES.get(
            'access_token') or JWTService.new_token_generator(refresh_token)
        if not (payload := JWTService.decode_token(token)):
            return Response({'error': 'Invalid JWT token'}, status=status.HTTP_401_UNAUTHORIZED)
        return payload['user_id']

    @cached_property
    def book_ids(self):
        return set(Book.get_all_id())

    def validate(self, attrs):
        attrs['user_id'] = self.get_user()
        book_id = attrs.get('book_id')
        if book_id not in self.book_ids():
            raise serializers.ValidationError(
                {'error': 'Book Doesnt Exist'})
        return attrs

    def get_edit_detail_url(self, instance):
        user_id = self.get_user()
        review_id = instance['review_id']
        url = reverse_lazy('account:reviews-detail',
                           kwargs={'user_id': user_id, 'id': review_id})
        return self.context['request'].build_absolute_uri(url)

    def to_representation(self, instance) -> Dict[str, Any]:
        representation = super().to_representation(instance)
        view = self.context.get('view')

        match view.action:
            case 'list':
                representation = {
                    'Book Detail': self.get_detail_url(instance, view_name="book:book-detail", lookup_field='book_id'),
                    'Book ID': instance['book_id'],
                    'Book Title': instance['book_title'],
                    'Rating': instance['rating'],
                    'Edit': self.get_edit_detail_url(instance)
                }
            case 'retrieve':
                representation = {
                    'Book ID': instance['book_id'],
                    'Rating': instance['rating'],
                }
        return representation
