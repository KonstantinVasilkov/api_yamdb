from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from rest_framework.renderers import JSONRenderer

from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import permissions, filters
from rest_framework.pagination import PageNumberPagination 
from requests.models import Response
from rest_framework.decorators import api_view, renderer_classes

from .models import User
from .serializers import UserSerializer, TokenSerializer
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .permissions import AdminOrOwnDataAccess

@api_view(['POST'])
@renderer_classes([JSONRenderer])
def token_obtain(request):
    SAMPLE_CODE = 'ABC'
    username = request.data['username']
    code = 'ABC'
    user=get_object_or_404(User, username=username)

    def verify_code(code):
        return code == SAMPLE_CODE

    if not verify_code(code):
        raise TypeError('Your code is incorrect')


    refresh = RefreshToken.for_user(user)
    token = {
        'token': str(refresh.access_token)
    }
    return Response(token, status=status.HTTP_200_OK)


@api_view(['POST'])
@renderer_classes([JSONRenderer])
def signup(request):
    username = request.data['username']
    email = request.data['email']
    confirmation_code = "ABC"
    SUBJECT = 'Код подтверждения'
    TEXT = f'Ваш код подтерждения: {confirmation_code}'
    FROM_FIELD = 'confirmation_code@yamdb.com'
    TO_FIELD = [email,]
    send_mail(
            SUBJECT,
            TEXT,
            FROM_FIELD,
            TO_FIELD,
            fail_silently=False, 
        )
    return Response(request.data, status=status.HTTP_200_OK)



class UserViewSet(ModelViewSet):

    serializer_class = UserSerializer
    filter_backends = (filters.SearchFilter,)
    permission_classes = (AdminOrOwnDataAccess,)

    def get_pagination_class(self):
        if self.request.resolver_match.url_name == 'individual_user-list':
            return None
        return PageNumberPagination

    pagination_class = property(fget=get_pagination_class)

    def get_queryset(self):
        if self.kwargs.get('username') == 'me':
            if self.request.user.is_authenticated:
                username = self.request.user.username
                return User.objects.filter(username=username)
            else:
                raise TypeError('You are not authenticated')
        elif self.kwargs.get('username'):
            print ("Детали пользователя:", self.request.user.is_authenticated, self.request.user.is_staff, self.request.user.is_superuser)
            return User.objects.filter(username=self.kwargs.get('username'))
        else:
            return User.objects.all()

    # потом будет либо IsAdminUser или собственный пермишен
    # permission_classes = (permissions.IsAdminUser,) 
    #pagination_class = LimitOffsetPagination
    
    # def_get_permissions(self, request): 
        # if request.user.role == 'admin':
            # return AdminOnly
        # else:
            # return permissions.


    # def perform_update(self, request, serializer):
        # serializer.is_valid(raise_exception=True)
        # if request.user.role=="admin" or request.user.is_superuser:
            # serializer.save()
        # else:
            # serializer.save(serializer.date.pop(**username)) # посмотреть, как было в kittigram


# class TokenView(TokenObtainPairView):
    # serializer_class = TokenSerializer



# class SignUpViewSet(ModelViewSet):
    # def send_code(self, request):
        # confirmation_code = "12345"
        # username = request.data["username"]
        # user = get_object_or_404(User, username=username)
        # email = user.email
        # send_mail(
            # 'Код подтверждения', # Subject
            # f'Ваш код подтерждения: {confirmation_code}', # Body
            # 'confirmation_code@yamdb.com',  # From
            # [email],  # To
            # fail_silently=False, 
        # )
