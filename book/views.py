from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from book import serailizers, models
from django.urls import reverse
from typing import Any, Dict, List
from tools.CustomAuthentication import JWTAuthentication
from account.permission import IsAuthenticatedOrRedirect
from rest_framework.decorators import action

from rest_framework.exceptions import PermissionDenied

class BookViewSet(viewsets.ViewSet):
    # permission_classes = [IsAuthenticatedOrRedirect,]
    authentication_classes = [JWTAuthentication]

    def get_permissions(self):
        action_permissions = {
            'list': [IsAuthenticatedOrRedirect],
            'retrieve': [IsAuthenticatedOrRedirect],
            'create': [IsAuthenticatedOrRedirect],
            'update': [IsAuthenticatedOrRedirect],
            'destroy': [IsAuthenticatedOrRedirect],
        }
        permission_classes = action_permissions.get(self.action, [permissions.AllowAny])
        return [permission() for permission in permission_classes]

   

 

    serializer_class = serailizers.BookSerializer
    lookup_field = 'id'

    def list(self, request, **kwargs) -> Response:
        filter_params = request.query_params.dict()
        ordering = request.query_params.get('ordering', None)

        if ordering:
            ordering = ordering.split(',')
            queryset = models.Book.all(
                filter=filter_params, ordering=ordering) if filter_params else models.Book.all(ordering=ordering)
        else:
            queryset = models.Book.all(
                filter=filter_params) if filter_params else models.Book.all()

        serializer = self.serializer_class(queryset, many=True, context={
                                           'request': request, 'view': self})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, id: int) -> Response:
        instance = models.Book.get_book_by_reviews(id)

        if not instance:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = self.serializer_class(
            instance, context={'request': request, 'view': self})
        return Response(serializer.data)

    def update(self, request, id: int = None) -> Response:
        instance = models.Book.get_book_by_reviews(id)
        if not instance:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(instance, data=request.data, context={
                                           'request': request, 'view': self})
        if serializer.is_valid():
            serializer.save()
            detail_url = serializer.get_detail_url(instance)
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED, headers={'Location': detail_url})

    def create(self, request) -> Response:
        serializer = self.serializer_class(data=request.data, context={
                                        'request': request, 'view': self})
        if serializer.is_valid():
            validated_data = serializer.validated_data

            obj_list = models.Book.insert(**validated_data)[0]
            instance = models.Book.get_book_by_reviews(book_id=obj_list['id'])
            serializer = self.serializer_class(
                instance, context={'request': request, 'view': self})
            detail_url = serializer.get_detail_url(instance)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers={'Location': detail_url})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

    def destroy(self, request, id: int) -> Response:
        instance = models.Book.get(id=id)[0]
        if not instance:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = self.serializer_class(
            instance, context={'request': request, 'view': self})
        models.Book.destroy(id=id)
        models.Review.destroy(book_id=id)
        list_url = serializer.get_list_url()
        return Response({'message': 'Book deleted successfully'}, status=status.HTTP_200_OK, headers={'Location': list_url})
    

  
