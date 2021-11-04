from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, profile

# from rest_framework_simplejwt.views import (
    # TokenObtainPairView
# )

app_name = 'users'

router_v1 = DefaultRouter()

# router_v1.register(r'users/(?P<username>[\w.@+-]+)/', UserViewSet, basename='user_detail')
router_v1.register(r'users/(?P<username>[\w.@+-]+)', UserViewSet, basename='user')

router_v1.register('users', UserViewSet, basename = 'users')


urlpatterns = [
    #path('users/me/', profile, name='profile'),
    path('', include(router_v1.urls))
]

    # path('auth/token/', views.TokenView.as_view(), name='token_obtain'),
    # path('auth/signup/', views.SignUpView.as_view(), name='confirmanation_code_obtain'),
