from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from requests.models import Response
from rest_framework import filters, permissions, status
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.pagination import PageNumberPagination
from rest_framework.renderers import JSONRenderer
from rest_framework.decorators import action

from rest_framework import status
from rest_framework.viewsets import ModelViewSet, GenericViewSet
# from rest_framework.mixins import RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin
                    
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import User
from .serializers import UserSerializer, TokenSerializer
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .permissions import AdminOrOwnProfile

@api_view(['POST'])
@renderer_classes([JSONRenderer])
def token_obtain(request):
    SAMPLE_CODE = 'ABC'
    username = request.data['username'] or None
    code = request.data['confirmation_code']
    user=get_object_or_404(User, username=username)

    def verify_code(code):
        return code == SAMPLE_CODE

    if not verify_code(code):
        data = {
                "error": [
                "Проверочный код неверный"
                ]
        }
        return Response(data, status=status.HTTP_400_BAD_REQUEST)

    refresh = RefreshToken.for_user(user)
    token = {
        'token': str(refresh.access_token)
    }
    return Response(token, status=status.HTTP_200_OK)


@api_view(['POST'])
@renderer_classes([JSONRenderer])
def signup(request):
    email = request.data['email']
    username = request.data['username']
    confirmation_code = "ABC"

    # ЗДЕСЬ нужно обязательно реализовать проверку, что e-mai это e-mail, и что оба поля не пустые!!

    SUBJECT = 'Код подтверждения'
    TEXT = f'Ваш код подтерждения: {confirmation_code}'
    FROM_FIELD = 'confirmation_code@yamdb.com'
    TO_FIELD = [email,]

    try:
        user=get_object_or_404(User, username=username)
    except:
        try:
            User.objects.create(username=username, email=email)
        except:
            data = {"error": ["e-mail не совпадает со значением в БД"]}
            return Response(data, status=status.HTTP_400_BAD_REQUEST)
    send_mail(
        SUBJECT,
        TEXT,
        FROM_FIELD,
        TO_FIELD,
        fail_silently=False,
    )
    return Response(request.data, status=status.HTTP_200_OK)


class UserViewSet(ModelViewSet):
# class UserViewSet(RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin, GenericViewSet):

    serializer_class = UserSerializer
    filter_backends = (filters.SearchFilter,)
    permission_classes = (AdminOrOwnProfile,)
    #http_method_names = ('get', 'patch',)
    lookup_field = "username"

    def get_pagination_class(self):
        if self.request.method != 'list':
            return None
        return PageNumberPagination

    pagination_class = property(fget=get_pagination_class)

    # def get_queryset(self):
        # if self.kwargs.get('username') == 'me':
            # if self.request.user.is_authenticated:
                # username = self.request.user.username)
                # return User.objects.get(username=username)
            # else:
                # raise TypeError('You are not authenticated')
        # elif self.kwargs.get('username'):
            # return User.objects.filter(username=self.kwargs.get('username'))
        # else:
            # return User.objects.all()
    queryset = User.objects.all()

    # @action(detail=True, url_path='me')
    # def me(self, request):
        # username = self.request.user.username
        # me = User.objects.filter(username=username)
        # serializer = self.get_serializer(me, many=False)
        # return Response(serializer.data) 

    def retrieve(self, request, username=None):
        queryset = User.objects.all()
        if username == 'me':
            username = self.request.user.username
        user = get_object_or_404(queryset, username=username)
        serializer = UserSerializer(user)
        return Response(serializer.data) 

    #@action(methods=['patch'])
    # def perform_update(self, serializer):
        # serializer.is_valid(raise_exception=True)
        # print ("serializer data =", serializer.data)
        # if serializer.instance.role=="admin" or serializer.instance.is_superuser or serializer.instance.is_staff:
        # if serializer.instance.is_superuser or serializer.instance.is_staff:
            # serializer.save(serializer.data)
        # else:
            # m = serializer.validated_data
            # print ("Было", m)
            # print("Стало:", m.pop('role'))
            # serializer.save(m)
