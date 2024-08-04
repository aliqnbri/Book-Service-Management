
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status,permissions
from .models import User , Review
from account import permission, serializers
from book import serailizers
from tools.CustomAuthentication import JWTAuthentication ,JWTService
from rest_framework.decorators import action
from django.shortcuts import redirect
from django.contrib.auth import login



    
class UserViewSet(viewsets.ViewSet):
    authentication_classes = [JWTAuthentication]
    lookup_field = 'id'


    def get_permissions(self):
        action_permissions = {
            'list': [permissions.AllowAny],
            'retrieve': [permission.IsAuthenticatedOrRedirect],
            'create': [permission.IsAuthenticatedOrRedirect],
            'update': [permission.IsAuthenticatedOrRedirect],
            'destroy': [permission.IsAuthenticatedOrRedirect],
            'suggest': [permission.IsAuthenticatedOrRedirect],
            'login': [permissions.AllowAny],
            'register': [permissions.AllowAny]
        }
        permission_classes = action_permissions.get(self.action, [permissions.AllowAny])
        return [permission() for permission in permission_classes]
    
    def get_serializer_class(self):
        action_serializers = {
            'register': serializers.RegisterSerializer,
            'suggest': serailizers.BookSerializer,
            'login': serializers.LoginSerializer
        }
        return action_serializers.get(self.action, serializers.UserSerializer)

   
            
    def get_serializer(self, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        return serializer_class(*args, **kwargs)        
            
        

    @action(detail=False, methods=['post'], url_path='register')
    def register(self, request):
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        serializer.create(validated_data)
        return Response(
            {'message': 'User Created Successfully', 'data': serializer.data},
            status=status.HTTP_201_CREATED,
        )

    @action(detail=False, methods=['post'], url_path='login')
    def login(self, request):
        serializer = self.get_serializer(data = request.data)
        serializer.is_valid(raise_exception=True)
        dict_instance = User.get(username=serializer.validated_data['username'])[0]
        access_toekn, refresh_token  = JWTService.token_generator(dict_instance), JWTService.refresh_token_generator(dict_instance)
        response = redirect(f"/users/{dict_instance['id']}/")
        response.set_cookie('access_token', access_toekn, httponly=True)
        response.set_cookie('refresh_token', refresh_token, httponly=True)
        return response
        

    def list(self, request):
        filter_params = request.query_params.dict()
        ordering = request.query_params.get('ordering', None)
        if ordering:
            ordering = ordering.split(',')
            queryset = User.all_users(
                filter=filter_params, ordering=ordering) if filter_params else User.all_users(ordering=ordering)
        else:
            queryset = User.all_users(
                filter=filter_params) if filter_params else User.all_users()
            
        serializer = self.get_serializer(queryset, many=True, context={
                                           'request': request, 'view': self})
        return Response(serializer.data, status=status.HTTP_200_OK)
        
    
    def retrieve(self, request, id: int) -> Response:
        user_data = User.get_by_reviews(user_id=id)
        if not user_data:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(user_data, context={'request': request, 'view': self})
    
        return Response(serializer.data, status=status.HTTP_200_OK)
    

    
    @action(methods=['get'], detail=True, url_path='suggest', url_name='suggest')
    def suggest(self, request, id=None):
        recommended_books = User.recommend_books(user_id=id)

        if isinstance(recommended_books, str):
            return Response({"detail": recommended_books}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(recommended_books, many=True, context={'request': request, 'view': self})
        return Response(serializer.data, status=status.HTTP_200_OK)
   
    
from rest_framework.reverse import reverse


class ReviewViewSet(viewsets.ViewSet):
    permission_classes = [permissions.AllowAny]
    lookup_field ='id'
    serializer_class = serializers.ReviewSerializer


    
    def list(self, request,**kwargs):
        user_id = kwargs.get('user_id')
        if not (user_data := User.get_by_reviews(user_id=user_id)):
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        instance = user_data['reviews']
    
        serializer = self.serializer_class(instance, many=True, context={
                                           'request': request, 'view': self})
      
        
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, id=None, **kwargs):
        kwargs.pop('user_id')
        review = Review.get(id=id)
        # review = Review.get_book_title(review_id=id)
        if not review:
            return Response({'error': 'Review not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(review[0], context={'request': request, 'view': self})
        return Response(serializer.data, status=status.HTTP_200_OK)



    def create(self,  request, user_id=None):
    
        serializer = self.serializer_class(data=request.data, context={
                                        'request': request, 'view': self})
  
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
    


        review = Review.insert(**validated_data)
        
        return Response({'message': 'Review created successfully', 'detail': review}, status=status.HTTP_201_CREATED)

    def destroy(self, request, user_id=None, id= None):
        review = Review.get(id=id)
       
        self.serializer_class(
            review, context={'request': request, 'view': self})
        
        Review.destroy(id =id)
        review_list_url = request.build_absolute_uri(
            reverse('account:reviews-list', kwargs={'user_id': user_id})
        )
        return Response({'message': 'Review deleted successfully','redirect_url': review_list_url}, status=status.HTTP_200_OK,headers={'Location': reverse('account:reviews-list', kwargs={'user_id': user_id})})
    
    def update(self, request, user_id=None, id=None):
        review =  Review.get(user_id=user_id)[0]
        if not review:
            return Response({'error': 'Review not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(review, data=request.data,context={'request': request, 'view': self})
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        Review.update(id=id, **validated_data)
        return Response({'message': 'Review updated successfully'}, status=status.HTTP_200_OK)

