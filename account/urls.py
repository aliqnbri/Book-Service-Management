from django.urls import path,include
from .views import RegisterView, LoginView,UserViewSet, ReviewViewSet ,SuggestView
from rest_framework.routers import DefaultRouter

app_name = 'account'
router = DefaultRouter()
router.register(r'user', UserViewSet, basename='user')
router.register(r'review', ReviewViewSet, basename='review')

urlpatterns = [
    path('user/register/', RegisterView.as_view(), name='register'),
    path('user/login/', LoginView.as_view(), name='login'),
    path('user/<int:id>/suggest/', SuggestView.as_view(), name='user-suggest'),
    path('', include(router.urls,)),

]
