from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from requests.models import Response
from rest_framework import exceptions, filters, status
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.pagination import PageNumberPagination
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.tokens import RefreshToken

from django.conf import settings
from .models import User
from .permissions import AdminOrOwnProfile
from .serializers import UserSerializer
from .utils import check_email, verify_code, check_username


@api_view(['POST'])
@renderer_classes([JSONRenderer])
def token_obtain(request):
    errors = False
    error_404 = False
    error_fields = {
        'username': [],
        'confirmation_code': []
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
            'Отсутствует поле confirmation_code'
        )
        confirmation_code = ''

    try:
        user = get_object_or_404(User, username=username)
    except Exception:
        error_404 = True
        user = None

    if error_404 and not errors:
        return Response('username не найден', status=status.HTTP_404_NOT_FOUND)

    if errors:
        return Response(error_fields, status=status.HTTP_400_BAD_REQUEST)

    if not verify_code(confirmation_code):
        errors = True
        error_fields['confirmation_code'].append('confirmation_code неверный')
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
    error_fields = {
        'email': [check_email(email)],
        'username': [check_username(username)]
    }
    if (type(error_fields['email'][0]) == str
            or type(error_fields['username'][0]) == str):
        return Response(error_fields, status=status.HTTP_400_BAD_REQUEST)
    send_mail(
        settings.SUBJECT,
        settings.TEXT,
        settings.FROM_FIELD,
        [email, ],
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
                and not self.request.user.is_admin):
            serializer.save(role=role)
        else:
            super().perform_update(serializer)
