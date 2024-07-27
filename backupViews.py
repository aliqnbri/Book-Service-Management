from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics, permissions
from .account.models import Users ,Reviews
from account import serializers


from .account.storage import Storage
from .account.recommendations import recommend_books
from rest_framework.decorators import action

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

from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token

class LoginView(APIView):
    serializer_class = serializers.LoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user_id = serializer.validated_data['id'] 
          
    
            return Response({"message": "Authenticated successfully","url": f"/reviews/?user_id={user_id}"},status=status.HTTP_200_OK)
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)

from django.urls import reverse
from rest_framework import viewsets

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
      
    @action(detail=True, methods=['get'], url_path='user/(?P<user_id>[^/.]+)')
    def list_user_reviews(self, request, user_id=1):
        if user_id is None:
            return Response({"detail": "User ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        user_reviews = Storage().get_user_reviews(user_id=1)
        
        if len(user_reviews) < 1:
            return Response({"detail": "There is not enough data about you."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Get recommended books
        recommended_books = recommend_books(user_id, Storage())
        
        if isinstance(recommended_books, str):
            return Response({"detail": recommended_books}, status=status.HTTP_400_BAD_REQUEST)
        
        # Serialize the recommended books
        book_serializer = serializers.BookSerializer(recommended_books, many=True)
        
        # Prepare response data
        response_data = {
            'user_reviews': user_reviews,
            'recommended_books': book_serializer.data,
            'book_list_url': request.build_absolute_uri(reverse('book-list')),
            'recommendation_url': request.build_absolute_uri(reverse('review-user-recommendations', args=[user_id]))
        }
        
        return Response(response_data, status=status.HTTP_200_OK)




        # user_data = Users.get_reviews(user_id=user_id)
        # serializer_class = self.get_serializer_class()
        # serializer = serializer_class(data=user_data, context={'request': request})
        # serializer.is_valid(raise_exception=True)
        # return Response(serializer.data, status=status.HTTP_200_OK)
    

    def list(self , request ,user_id=None):
        user_data = Users.get_reviews(user_id=1)
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(data=user_data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


    

    # def retrieve(self, request, id=None):
        
  
    #     review = Reviews.get_object(id=id).to_dict()
    #     serializer_class = self.get_serializer_class()
    #     serializer = serializer_class(review, context={'request': request})

    #     return Response(serializer.data, status=status.HTTP_200_OK)
    

    def update(self, request, id=None):
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            review = Reviews.get_object(id=id)
            dict_review = review.to_dict()
            updated_review = serializer.update(dict_review, serializer.validated_data)
            print(updated_review)
      
            Reviews.update(review,**updated_review)
          
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
        
    



