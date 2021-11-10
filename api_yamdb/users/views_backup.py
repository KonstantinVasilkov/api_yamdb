from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from requests.models import Response
from rest_framework import filters, status
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.pagination import PageNumberPagination
from rest_framework.renderers import JSONRenderer
from rest_framework import exceptions
from django.core.exceptions import ValidationError

from rest_framework import status
from rest_framework.viewsets import ModelViewSet

from .models import User
from .serializers import UserSerializer
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .permissions import AdminOrOwnProfile

from django.core.validators import validate_email
from django.core.validators import validate_slug as validate_username
from django.contrib.auth.validators import (
    UnicodeUsernameValidator as validate_username)


@api_view(['POST'])
@renderer_classes([JSONRenderer])
def token_obtain(request):
    SAMPLE_CODE = 'ABC'
    errors = False
    error_404 = False
    error_fields = {
        "username": [],
        "confirmation_code": []
    }
    if 'username' in request.data:
        username = request.data['username']
    else:
        errors = True
        error_fields['username'].append('Отсутствует поле username')
        username = None

    if 'confirmation_code' in request.data:
        confirmation_code = request.data['confirmation_code']
    else:
        errors = True
        error_fields['confirmation_code'].append(
            'Отсутствует поле confrimation_code')
        confirmation_code = ''

    def verify_code(value):
        return value == SAMPLE_CODE

    try:
        user = get_object_or_404(User, username=username)
    except Exception:
        error_404 = True
        user = None

    if error_404 and not errors:
        return Response("username не найден", status=status.HTTP_404_NOT_FOUND)

    if errors:
        return Response(error_fields, status=status.HTTP_400_BAD_REQUEST)

    if not verify_code(confirmation_code):
        errors = True
        error_fields['confirmation_code'].append('confrimation_code неверный')
        return Response(error_fields, status=status.HTTP_400_BAD_REQUEST)

    refresh = RefreshToken.for_user(user)
    token = {
        'token': str(refresh.access_token)
    }
    return Response(token, status=status.HTTP_200_OK)


@api_view(['POST'])
@renderer_classes([JSONRenderer])
def signup(request):
    email = ''
    username = ''
    if 'email' in request.data:
        email = request.data['email']
    if 'username' in request.data:
        username = request.data['username']
    SUBJECT = 'Код подтверждения'
    confirmation_code = "ABC"
    TEXT = f'Ваш код подтерждения: {confirmation_code}'
    FROM_FIELD = 'confirmation_code@yamdb.com'
    TO_FIELD = [email, ]
    errors = False
    error_fields = {
        "email": [],
        "username": []
    }
    try:
        validate_email(email)
    except ValidationError:
        errors = True
        error_fields['email'].append('Некорректно заполнен email')

    try:
        validate_username(username)
    except ValidationError:
        errors = True
        error_fields['username'].append('Некорректно заполнен username')

    if username == 'me' or username == '':
        errors = True
        error_fields['username'].append('Пустое значение и "me" недопустимы')

    try:
        get_object_or_404(User, username=username)
        errors = True
        error_fields['username'].append('Такой пользователь уже существует')
    except Exception:
        pass

    try:
        get_object_or_404(User, email=email)
        errors = True
        error_fields['email'].append('email уже существует')
    except Exception:
        pass

    if errors:
        return Response(error_fields, status=status.HTTP_400_BAD_REQUEST)
    send_mail(
        SUBJECT,
        TEXT,
        FROM_FIELD,
        TO_FIELD,
        fail_silently=False,
    )
    User.objects.create(username=username, email=email)
    return Response(request.data, status=status.HTTP_200_OK)


class UserViewSet(ModelViewSet):

    serializer_class = UserSerializer
    filter_backends = (filters.SearchFilter,)
    permission_classes = (AdminOrOwnProfile,)
    lookup_field = 'username'

    def get_pagination_class(self):
        if self.request.method != 'list':
            return None
        return PageNumberPagination

    def get_queryset(self):
        if self.kwargs.get('username') == 'me':
            if self.request.user.is_authenticated:
                username = self.request.user.username
                self.kwargs['username'] = username
                return User.objects.filter(username=username)
            else:
                raise TypeError('You are not authenticated')
        elif self.kwargs.get('username'):
            return User.objects.filter(username=self.kwargs.get('username'))
        else:
            return User.objects.all()

    def perform_destroy(self, object):
        if ('username' in self.request.resolver_match.kwargs
                and self.request.resolver_match.kwargs['username'] == 'me'):
            raise exceptions.MethodNotAllowed(
                'delete', detail='нельзя удалить самого себя')
        super().perform_destroy(object)

    def perform_update(self, serializer):
        role = self.request.user.role
        if (self.request.user.is_authenticated
                and role != 'admin'
                and not self.request.user.is_staff
                and not self.request.user.is_superuser):
            serializer.save(role=role)
        else:
            super().perform_update(serializer)
