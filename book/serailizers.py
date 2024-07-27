from rest_framework import serializers
from .models import Books
from django.urls import reverse


class ReviewSerializer(serializers.Serializer):
    rating = serializers.IntegerField()
    username = serializers.CharField(max_length=200)

    class Meta:
        fields = ['rating']


class BookSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    detail_url = serializers.HyperlinkedIdentityField(
        view_name='book:book-detail', lookup_field='id',read_only=False)
    title = serializers.CharField(max_length=200)
    author = serializers.CharField(max_length=200)
    genre = serializers.CharField(max_length=200)

    reviews = serializers.SerializerMethodField()

    def get_reviews(self, instance):
        if hasattr(instance, 'reviews'):
            return [ReviewSerializer(review).data for review in instance.reviews]
        return []


    def to_representation(self, instance):
        request = self.context.get('request')
      
        instance = Books.create(**instance)
        list_url = request.build_absolute_uri(reverse('book:book-list',)) 
    
        return {
            'list': list_url,
            'id': instance.id,
            'title': instance.title,
            'author': instance.author,
            'genre': instance.genre,
            'reviews': self.get_reviews(instance)
           
        }

