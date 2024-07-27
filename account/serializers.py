from rest_framework import serializers
from account.models import Users, Reviews
from tools import HashPassword
from rest_framework.response import Response
from rest_framework import status
from tools.CustomAuthentication import authenticate
from django.urls import reverse
from tools.DatabaseConncetor import PsqlConnector


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


class UpdateReviewSerializer(serializers.Serializer):
    rating = serializers.IntegerField(min_value=1, max_value=5)

    def update(self, instance, validated_data):
        instance['rating'] = validated_data.get('rating', instance['rating'])
        return instance
    
    def create(self, validated_data):
        review = Reviews.update(**validated_data)
        return review
    
    
    def to_representation(self, instance):
        print(instance)
    
        return {
            'id': instance['id'],
            'detail_url': self.context['request'].build_absolute_uri(reverse('book:book-detail', args=[instance['book_id']])),
            'book_title': self.fetch_book_title(instance['book_id']),
            'rating': instance['rating'],
        }


class ReviewSerializer(BaseSerializer):
    id = serializers.IntegerField(read_only=True)
    book_title = serializers.CharField(read_only=True)
    rating = serializers.IntegerField(min_value=1, max_value=5)
    book_id = serializers.IntegerField(read_only=True)

    def to_representation(self, instance):
        # instance is a dictionary with review data
        review = instance
        book_id = review.get(
            'book_id', self.context['request'].parser_context['kwargs'].get('id'))
        book_title = self.fetch_book_title(book_id)

        return {
            'id': review['id'],
            'detail_url': self.get_detail_url(review, 'book:book-detail'),
            'book_title': book_title,
            'rating': review['rating'],

        }

    def update(self, instance, validated_data):
        for key, value in validated_data.items():
            if key in ['rating']:  # Add other fields you want to update here
                instance[key] = value
        return instance


class UserSerializer(BaseSerializer):
    id = serializers.IntegerField()
    book_list_url= serializers.SerializerMethodField()
    username = serializers.CharField()
    reviews = serializers.ListField()
    recommends = serializers.SerializerMethodField()

    class Meta:
        fields = ['id', 'book_list_url', 'username', 'reviews', 'recommends']



    def get_book_list_url(self,instance):
        request = self.context.get('request')
        return request.build_absolute_uri(reverse('book:book-list'))


    def get_recommends(self, instance):
        request = self.context.get('request')
        return request.build_absolute_uri(reverse('account:user-suggest', args=[instance['id']]))

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        reviews = instance.get('reviews', [])

        review_representations = [
            {
                'review_detail': self.get_detail_url(review, 'account:review-detail', 'id'),
                'book_detail_url': self.get_detail_url(review, 'book:book-detail'),
                'book_title': self.fetch_book_title(review['book_id']),
                'rating': review['rating'],
            }
            for review in reviews
        ]
        representation['reviews'] = review_representations
        representation['recommends'] = self.get_recommends(instance)

        

        return representation


class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=100)
    password = serializers.CharField(write_only=True, max_length=128)

    def validate_username(self, value: str) -> str:
        # Custom validation method to check if the username already exists
        if Users.get_object(username=value):
            raise serializers.ValidationError(f"User {value} already exists")
        return value

    def create(self, validated_data: dict) -> object:
        username = validated_data['username']
        password = validated_data['password']

        # Hash the password and insert the user
        hashed_password = HashPassword.hash_password(password)
        obj = Users.insert(username=username, password=hashed_password)
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
