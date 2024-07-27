from rest_framework import viewsets, permissions, status, views
from rest_framework.response import Response
from book.serailizers import BookSerializer
from .models import Books
import json,tools
from django.urls import reverse


class BookViewSet(viewsets.ViewSet):
    permission_classes = [permissions.AllowAny]
    serializer_class = BookSerializer
    lookup_field = 'id'


    def list(self, request, **kwargs):

        filter_params = request.query_params.dict()
        if filter_params:
            queryset = Books.all(filter=filter_params)
        else:
            queryset = Books.all()

        result = [
            {'detail': request.build_absolute_uri(
                reverse('book:book-detail', kwargs={'id': book.id})), **book.to_dict()}
            for book in queryset]

        # serializer = self.serializer_class(result,context={'request': request})

        return Response(result, status=status.HTTP_200_OK)



    def retrieve(self, request, id: int):
        instance = Books.get_book_with_reviews(id)

        serializer = self.serializer_class(
            instance, context={'request': self.request})
        return Response(serializer.data)


    def create(self, request):
        serializer = self.serializer_class(
            data=request.data, context={'request': self.request})

        if serializer.is_valid():
            validated_data = serializer.validated_data
            book = Books.insert(**validated_data)
            serializer = self.serializer_class(
                book, context={'request': self.request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, id=None):
        book = Books.get_object(id=id)
        if book:
            serializer = BookSerializer(book, data=request.data)
            if serializer.is_valid():

                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_404_NOT_FOUND)


class FilterableView(views.APIView):
    model = None
    serializer_class = None

    def get(self, request):
        filters = self.get_filters(request)
        objects = self.model.all(filters)
        serializer = self.serializer_class(objects, many=True)
        return Response(serializer.data)

    def get_filters(self, request):
        filters = request.query_params.get('filters')
        return json.loads(filters) if filters else {}
