from django.contrib.auth.models import AbstractUser
from django.db import models


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
    email = models.EmailField(blank=False, unique=True, null=False)

    @property
    def is_admin(self):
        return (
            self.role == self.ADMIN or self.is_superuser or self.is_staff
        )

    @property
    def is_moderator(self):
        return self.role == self.MODERATOR

    @property
    def is_user(self):
        return self.role == self.USER
