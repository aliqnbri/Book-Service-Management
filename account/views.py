
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status,permissions
from .models import User

from account import permission, serializers
from book import serailizers
from tools.CustomAuthentication import JWTAuthentication ,JWTService
from rest_framework.decorators import action
from django.shortcuts import redirect




    
class UserViewSet(viewsets.ViewSet):
    authentication_classes = [JWTAuthentication]
    lookup_field = 'id'


    def get_permissions(self):
        action_permissions = {
            'list': [permissions.IsAdminUser],
            'retrieve': [permission.IsAuthenticatedOrRedirect],
            'create': [permissions.IsAdminUser],
            'update': [permissions.IsAdminUser],
            'destroy': [permissions.IsAdminUser],
            'suggest': [permissions.IsAuthenticated],
            'login': [permissions.AllowAny],
            'register': [permissions.AllowAny]
        }
        permission_classes = action_permissions.get(self.action, [permission.AllowAny])
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
        token  = JWTService.token_generator(dict_instance)
        response = redirect(f"/users/{dict_instance['id']}/")
        response.set_cookie('jwt', token, httponly=True)
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
   
    


    



