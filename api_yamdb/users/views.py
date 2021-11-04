from django.core.mail import send_mail
from django.shortcuts import get_object_or_404

from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import permissions, filters
from rest_framework.pagination import PageNumberPagination 
from requests.models import Response

from .models import User
from .serializers import UserSerializer, TokenSerializer

def profile(request):
    pass
    # users = User.objects.all()
    # return render(request, 'users/profile.html', {'users': users})


class UserViewSet(ModelViewSet):

    # queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = PageNumberPagination 

    filter_backends = (filters.SearchFilter,)

    def get_queryset(self):
        if self.kwargs.get('username') == 'me':
            if self.request.user.is_authenticated:
                username = self.request.user.username
                return User.objects.filter(username=username)
            else:
                raise TypeError('You are not authenticated')
        elif self.kwargs.get('username'):
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
