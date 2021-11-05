from django.urls import path, include
from rest_framework.routers import DefaultRouter
# from .views import UserViewSet, TokenView, token_obtain
from .views import UserViewSet, token_obtain, signup

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

app_name = 'users'

router_v1 = DefaultRouter()

router_v1.register(r'users/(?P<username>[\w.@+-]+)', UserViewSet, basename='individual_user')
router_v1.register('users', UserViewSet, basename = 'users')


urlpatterns = [
    path('', include(router_v1.urls)),
    # path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    # path('auth/token/', TokenView.as_view(), name='token_obtain_pair'),
    path('auth/token/', token_obtain, name='token_obtain'),

    path('auth/signup/', signup, name='singup')
]

    # path('auth/token/', views.TokenView.as_view(), name='token_obtain'),
    # path('auth/signup/', views.SignUpView.as_view(), name='confirmanation_code_obtain'),
