from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from requests.models import Response
from rest_framework import filters, permissions, status
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.pagination import PageNumberPagination, LimitOffsetPagination
from rest_framework.renderers import JSONRenderer
from rest_framework.decorators import action
from rest_framework import exceptions
from django.core.exceptions import ValidationError

from rest_framework import status
from rest_framework.viewsets import ModelViewSet, GenericViewSet
# from rest_framework.mixins import RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin
                    
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import User
from .serializers import UserSerializer, TokenSerializer
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .permissions import AdminOrOwnProfile

from django.core.validators import validate_email
from django.core.validators import validate_slug as validate_username
from django.contrib.auth.validators import UnicodeUsernameValidator as validate_username


@api_view(['POST'])
@renderer_classes([JSONRenderer])
def token_obtain(request):
    SAMPLE_CODE = 'ABC'
    errors = False
    error_404 = False
    error_fields = {
        "username":[],
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
        error_fields['confirmation_code'].append('Отсутствует поле confrimation_code')
        confirmation_code = ''
    def verify_code(value):
        return value == SAMPLE_CODE

    if not verify_code(confirmation_code):
        errors = True
        error_fields['confirmation_code'].append('confrimation_code неверный')

    try:
        user=get_object_or_404(User, username=username)
    except:
        data = {"username": "Пустое поле username "}
        return Response(data, status=status.HTTP_404_NOT_FOUND)
        # return Response(data, status=status.HTTP_400_BAD_REQUEST)

    if errors:
        # data = {"error": error_fields}
        data = error_fields
        return Response(data, status=status.HTTP_400_BAD_REQUEST) 

    refresh = RefreshToken.for_user(user)
    token = {
        'token': str(refresh.access_token)
    }
    return Response(token, status=status.HTTP_200_OK)
    

@api_view(['POST'])
@renderer_classes([JSONRenderer])
def signup(request):
    if 'email' in request.data:
        email = request.data['email']
    else:
        email = ''
    if 'username' in request.data:
        username = request.data['username']
    else:
        username = ''
    confirmation_code = "ABC"

    SUBJECT = 'Код подтверждения'
    TEXT = f'Ваш код подтерждения: {confirmation_code}'
    FROM_FIELD = 'confirmation_code@yamdb.com'
    TO_FIELD = [email,]
    errors = False
    error_404 = False
    error_fields = {
        "email":[],
        "username": []
    }
    try:
        validate_email(email)
    except ValidationError as e:
        errors = True
        error_fields['email'].append('Некорректно заполнен email')
    try: 
        validate_username(username)
    except:
        errors = True
        error_fields['username'].append('Некорректно заполнен username')
    if username == 'me' or username == '':
        errors = True
        error_fields['username'].append('Пустое значение и "me" недопустимы')
    try:
        get_object_or_404(User, username=username)
        # т.е. если пользователь есть (не возник exception), то это ошибка
        errors = True
        error_fields['username'].append('Такой пользователь уже существует')     
    except:
        # создаем пользователя, как указано выше
        try:
            User.objects.create(username=username, email=email)
        # а вот если тут не получилось, значит, уже есть такой email
        except:
            errors = True
            error_fields['email'].append('email уже существует')  


    send_mail(
        SUBJECT,
        TEXT,
        FROM_FIELD,
        TO_FIELD,
        fail_silently=False,
    )
    # if error_404:
        # data = {'error': error_fields}
        # return Response(data, status=status.HTTP_404_NOT_FOUND)
    if errors:
        #data = {'error': error_fields}
        data = error_fields
        return Response(data, status=status.HTTP_400_BAD_REQUEST)
    return Response(request.data, status=status.HTTP_200_OK)



class UserViewSet(ModelViewSet):
# class UserViewSet(RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin, GenericViewSet):

    serializer_class = UserSerializer
    filter_backends = (filters.SearchFilter,)
    permission_classes = (AdminOrOwnProfile,)
    #http_method_names = ('get', 'patch',)
    lookup_field = 'username'
    # pagination_class = PageNumberPagination

    def get_pagination_class(self):
        if self.request.method != 'list':
            return None
        return PageNumberPagination
        # return LimitOffsetPagination
    
    # pagination_class = property(fget=get_pagination_class)

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
        print("Пробуем удалить объект, object.username = ", object.username)
        print("Пробуем удалить объект, kwargs = ", self.request.resolver_match.kwargs)
        if ('username' in self.request.resolver_match.kwargs 
            and self.request.resolver_match.kwargs['username'] == 'me'):
            raise exceptions.MethodNotAllowed('delete', detail='нельзя удалить самого себя')
            # return Response(self.request.data, status=status.HTTP_405_METHOD_NOT_ALLOWED) 
        super().perform_destroy(object)

    def perform_update(self, serializer):
        role = self.request.user.role
        if (self.request.user.is_authenticated
            and role != 'admin'
            and not self.request.user.is_staff
            and not self.request.user.is_superuser):
                # self.request.user.role = 'user'
                print ("Вот, что присваиваем: ")
                serializer.save(role=role)
        else:
            super().perform_update(serializer)

