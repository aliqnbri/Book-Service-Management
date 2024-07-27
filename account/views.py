from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework import viewsets
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics, permissions
from .models import Users, Reviews
from account import serializers
from django.urls import reverse


#
from .storage import Storage
from rest_framework.decorators import action

from book.serailizers import BookSerializer
from .recommend import recommend_books ,identify_favorite_genre


class RegisterView(generics.CreateAPIView):
    serializer_class = serializers.RegisterSerializer
    permission_classes = (permissions.AllowAny,)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response({
            'message': 'User Created Successfully',
            'data': serializer.data
        }, status=status.HTTP_201_CREATED, headers=headers)


class LoginView(APIView):
    serializer_class = serializers.LoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user_id = serializer.validated_data['id']

            return Response({"message": "Authenticated successfully", "url": f"/user/?user_id={user_id}"}, status=status.HTTP_200_OK)
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)
    


class SuggestView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = BookSerializer

    def get(self, request, id=None):
        if id is None:
            return Response({"detail": "User ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        recommended_books = recommend_books(id, Storage())

        if isinstance(recommended_books, str):
            return Response({"detail": recommended_books}, status=status.HTTP_400_BAD_REQUEST)

        book_serializer = self.serializer_class(recommended_books, many=True, context={'request': self.request} )

        response_data = {
            'recommended_books': book_serializer.data,
            'book_list_url': request.build_absolute_uri(reverse('book:book-list')),
            'recommendation_url': request.build_absolute_uri(reverse('account:user-suggest', args=[id]))
        }

        return Response(response_data, status=status.HTTP_200_OK)

    



class UserViewSet(viewsets.ViewSet):
    permission_classes = [permissions.AllowAny]
    lookup_field = 'id'

    def get_serializer_class(self):
        match self.action:
            case 'list':
                return serializers.UserSerializer
            case 'update':
                return serializers.UpdateReviewSerializer
            case _:
                return serializers.ReviewSerializer



    def list(self, request, user_id=None):
        user_data = Users.get_reviews(user_id=1)

        serializer_class = self.get_serializer_class()
        serializer = serializer_class(
            data=user_data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, id=None):
        user_data = Users.get_reviews(user_id=1)

        serializer_class = self.get_serializer_class()
        serializer = serializer_class(
            data=user_data, context={'request': request})
        serializer.is_valid(raise_exception=True)
       

        return Response(serializer.data, status=status.HTTP_200_OK)


    def update(self, request, id=None):
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(
            data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            review = Reviews.get_object(id=id)
            dict_review = review.to_dict()
            updated_review = serializer.update(
                dict_review, serializer.validated_data)
            print(updated_review)

            Reviews.update(review, **updated_review)

            return Response(updated_review, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=400)

    def destroy(self, request, id=None):
        if id is None:
            return Response({'error': 'Review ID is required'}, status=status.HTTP_400_BAD_REQUEST)

        review = Reviews.get_object(id=id)
        if not review:
            return Response({'error': 'Review not found'}, status=status.HTTP_404_NOT_FOUND)

        Reviews.destroy(review)
        return Response({'message': 'Review deleted successfully'}, status=status.HTTP_204_NO_CONTENT)


# class ReviewViewSet(viewsets.ViewSet):
#     permission_classes = [permissions.AllowAny]
#     lookup_field = 'id'

#     def get_serializer_class(self):
#         match self.action:
#             case 'list':
#                 return serializers.UserSerializer
#             case 'update':
#                 return serializers.UpdateReviewSerializer
#             case _:
#                 return serializers.ReviewSerializer

#     def list(self, request, user_id=None):
#         user_data = Users.get_reviews(user_id=1)
#         serializer_class = self.get_serializer_class()
#         serializer = serializer_class(
#             data=user_data, context={'request': request})
#         serializer.is_valid(raise_exception=True)
#         return Response(serializer.data, status=status.HTTP_200_OK)

#     def retrieve(self, request, id=None):

#         review = Reviews.get_object(id=id).to_dict()
#         serializer_class = self.get_serializer_class()
#         serializer = serializer_class(review, context={'request': request})

#         return Response(serializer.data, status=status.HTTP_200_OK)

#     def update(self, request, id=None):
#         serializer_class = self.get_serializer_class()
#         serializer = serializer_class(
#             data=request.data, partial=True, context={'request': request})
#         if serializer.is_valid():
#             review = Reviews.get_object(id=id)
#             dict_review = review.to_dict()
#             updated_review = serializer.update(
#                 dict_review, serializer.validated_data)
#             print(updated_review)

#             Reviews.update(review, **updated_review)

#             return Response(updated_review, status=status.HTTP_200_OK)
#         return Response(serializer.errors, status=400)

#     def destroy(self, request, id=None):
#         if id is None:
#             return Response({'error': 'Review ID is required'}, status=status.HTTP_400_BAD_REQUEST)

#         review = Reviews.get_object(id=id)
#         if not review:
#             return Response({'error': 'Review not found'}, status=status.HTTP_404_NOT_FOUND)

#         Reviews.destroy(review)
#         return Response({'message': 'Review deleted successfully'}, status=status.HTTP_204_NO_CONTENT)


    



