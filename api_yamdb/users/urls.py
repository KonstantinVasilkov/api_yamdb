from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, token_obtain, signup


app_name = 'users'

router_v1 = DefaultRouter()
router_v1.register(r'users', UserViewSet, basename='users')

urlpatterns = [
    path('', include(router_v1.urls)),
    path('auth/token/', token_obtain, name='token_obtain'),
    path('auth/signup/', signup, name='singup')
]
