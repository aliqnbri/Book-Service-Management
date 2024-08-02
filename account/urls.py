from django.urls import path,include
from .views import UserViewSet
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)




app_name = 'account'
router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
# router.register(r'review', ReviewViewSet, basename='review')


urlpatterns = [
    path('', include(router.urls,)),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),



]
