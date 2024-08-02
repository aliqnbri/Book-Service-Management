from rest_framework.permissions import BasePermission
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework import status
from django.urls import reverse
from tools.CustomAuthentication import JWTService
class IsAuthenticatedOrRedirect(BasePermission):
    def has_permission(self, request, view):
        token = request.META.get('HTTP_AUTHORIZATION') or request.COOKIES.get('jwt')
        if not token or not JWTService.is_token_valid(token):
            login_url = reverse('user-login')  # URL name for your login view
            response = Response({"detail": "Authentication credentials were not provided. Please log in.", "login_url": login_url}, status=status.HTTP_401_UNAUTHORIZED)
            view.response = response  # Store the response for use in the view
            return False
        return True



def get_permissions(self):
    match self.action:
        case 'list':
            permission_classes = [permissions.IsAdminUser]
        case 'retrieve':
            permission_classes = [IsAuthenticatedOrRedirect]
        case 'create':
            permission_classes = [permissions.IsAdminUser]
        case 'update':
            permission_classes = [permissions.IsAdminUser]
        case 'destroy':
            permission_classes = [permissions.IsAdminUser]
        case 'suggest':
            permission_classes = [permissions.IsAuthenticated]
        case 'login':
            permission_classes = [permissions.AllowAny]
        case 'register':
            permission_classes = [permissions.AllowAny]
            
    return [permission() for permission in permission_classes]    