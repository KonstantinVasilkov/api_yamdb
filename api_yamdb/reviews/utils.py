from django.utils import timezone
from rest_framework.exceptions import ValidationError


def year_validator(value):
    year = timezone.now().year
    if 0 < value > year:
        raise ValidationError(
            f'{value} Неправильный год!'
        )
