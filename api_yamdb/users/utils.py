from django.core.validators import validate_email
from django.core.validators import validate_slug as validate_username
from django.core.exceptions import ValidationError

from django.conf import settings
from .models import User


def check_username(value):
    try:
        validate_username(value)
        if value == 'me' or not value:
            return 'Имя пользователя не может быть me или пустым'
        if User.objects.filter(username=value).exists():
            return 'Пользователь уже существует'
        return True
    except ValidationError:
        return 'Некорректный username'


def check_email(value):
    try:
        validate_email(value)
        if not value:
            return 'email не может быть пустым'
        if User.objects.filter(email=value).exists():
            return 'email уже есть в базе'
        return True
    except ValidationError:
        return 'Некорректный email'


def verify_code(value):
    return value == settings.CONFIRMATION_CODE_SAMPLE
