from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    USER = 'user'
    MODERATOR = 'moderator'
    ADMIN = 'admin'
    USER_ROLES = [
        (USER, 'The ordinary user'), 
        (MODERATOR, 'User with content edit privileges'),
        (ADMIN, 'Full rights user'),
    ]
    role = models.CharField(
        max_length=10, 
        choices=USER_ROLES,
        default=USER
    )    
    bio = models.TextField(
        'Биография',
        blank=True,
    )
    email = models.EmailField(blank=False)