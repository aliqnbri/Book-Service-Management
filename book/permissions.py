from rest_framework.permissions import BasePermission, SAFE_METHODS

from rest_framework import permissions




def get_permissions(self):
    match self.action:
        case 'list':
            permission_classes = [permissions.AllowAny]
        case 'etrieve':
            permission_classes = [permissions.IsAuthenticated]
        case 'create':
            permission_classes = [permissions.IsAdminUser]
        case 'update':
            permission_classes = [permissions.IsAdminUser]
        case 'destroy':
            permission_classes = [permissions.IsAdminUser]
        case _:
            permission_classes = [permissions.AllowAny]
            
    return [permission() for permission in permission_classes]    