from rest_framework import serializers
from .models import Book
from django.urls import reverse


class SimpleReviewSerializer(serializers.Serializer):
    user = serializers.CharField(max_length=200)
    rating = serializers.IntegerField()






class BookSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    detail_url = serializers.SerializerMethodField()
    title = serializers.CharField(max_length=200)
    author = serializers.CharField(max_length=200)
    genre = serializers.CharField(max_length=200)
    # reviews = serializers.SerializerMethodField()



    def update(self, instance, validated_data):
        updated_instance:dict = Book.update(instance['id'], **validated_data)
        updated_instance = Book.get_book_by_reviews(updated_instance['id'])
        return updated_instance


    def get_detail_url(self, obj):
        request = self.context.get('request')
        return request.build_absolute_uri(reverse('book:book-detail', kwargs={'id': int(obj['id'])}))


    def get_reviews(self, instance):
            return [SimpleReviewSerializer(review).data for review in instance['reviews']]


    def to_representation(self, instance):
        representation = super().to_representation(instance)
        request = self.context.get('request')
        view = self.context.get('view')

        match view.action:
            case 'list':
                representation.pop('reviews', None)
            case 'retrieve' | 'update':
                representation.pop('detail_url')
                list_url = request.build_absolute_uri(reverse('book:book-list'))
                representation = {'list_url': list_url, **representation}
                # representation['list_url'] = request.build_absolute_uri(reverse('book:book-list'))
                representation['reviews'] = self.get_reviews(instance)

        return representation

