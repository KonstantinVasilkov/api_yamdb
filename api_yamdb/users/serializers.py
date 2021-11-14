from rest_framework import serializers

from .models import User


class UserSerializer(serializers.ModelSerializer):

    def validate_username(self, value):
        if value == 'me':
            raise TypeError('Значение "me" зарезервировано')
        return value

    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name', 'last_name', 'bio', 'role'
        )
        required_fields = ('username', 'email',)
