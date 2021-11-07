from rest_framework import serializers
from rest_framework.relations import SlugRelatedField
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import User


class UserSerializer(serializers.ModelSerializer):

    def validate_username(self, value):
        if value == 'me':
            raise TypeError ('me is reserved name')
        return value


    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'bio','role')
        required_fields = ('username', 'email',)


class TokenSerializer(TokenObtainPairSerializer):
    token=serializers.CharField(source='access')
    
    class Meta:
        fields = ('token')
    # fields = 'token'

    def get_token(self, user):
        refresh = RefreshToken.for_user(user)
        return {'token': str(refresh.access_token)}