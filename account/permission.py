from rest_framework.permissions import BasePermission
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework import status
from django.urls import reverse
from tools.CustomAuthentication import JWTService
from django.shortcuts import redirect



class IsAuthenticatedOrRedirect(BasePermission):
    def has_permission(self, request, view):
        if not (token :=request.COOKIES.get('access_token')) :
            if  not (JWTService.is_token_valid(token)):
                login_url = reverse('account:user-login')  # URL name for your login view
                view.response = redirect(login_url)  # Store the response for use in the view
                return False
        return True

