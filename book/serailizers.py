from rest_framework import serializers
from .models import Book
from django.urls import reverse_lazy
from typing import Any, Dict, List


class SimpleReviewSerializer(serializers.Serializer):
    user = serializers.CharField(read_only=True)
    rating = serializers.IntegerField()



class BookSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    detail_url = serializers.SerializerMethodField()
    title = serializers.CharField(max_length=200)
    author = serializers.CharField(max_length=200)
    genre = serializers.CharField(max_length=200)

    def update(self, instance, validated_data):
        updated_instance: dict = Book.update(instance['id'], **validated_data)
        updated_instance = Book.get_book_by_reviews(updated_instance['id'])
        return updated_instance

    def get_detail_url(self, instance: Book) -> str:
        request = self.context.get('request')
        return request.build_absolute_uri(reverse_lazy('book:book-detail', kwargs={'id': instance['id']}))

    def get_list_url(self) -> str:
        request = self.context.get('request')
        return request.build_absolute_uri(reverse_lazy('book:book-list'))

    def get_reviews(self, instance: Book) -> List[Dict[str, Any]]:
        return [SimpleReviewSerializer(review).data for review in instance['reviews']]

    def to_representation(self, instance: Book) -> Dict[str, Any]:
        representation = super().to_representation(instance)
        view = self.context.get('view')

        match view.action:
            case 'list' | 'destroy':
                representation.pop('reviews', None)
            case 'retrieve' | 'create':
                representation.pop('detail_url')
                representation = {
                    'list_url': self.get_list_url(), **representation}
                representation['reviews'] = self.get_reviews(instance)
            case 'update':
                representation['reviews'] = self.get_reviews(instance)

        return representation
