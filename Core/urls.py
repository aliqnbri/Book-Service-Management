
from django.contrib import admin
from django.urls import path, include
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView


class APIRootView(APIView):
    def get(self, request, format=None):
        return Response({
            'users': reverse('account:user-list', request=request, format=format),
            'books': reverse('book:book-list', request=request, format=format),
        })

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),
    path('', include([
        path('', APIRootView.as_view(), name='api-root'),
        path('', include('account.urls', namespace='account')),
        path('', include ('book.urls', namespace='book'))
    ]))
]












