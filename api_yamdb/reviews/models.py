from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from users.models import User


class Titles(models.Model):
    name = models.CharField(
        max_length=256,
        verbose_name='Произведение',
    )


class Reviews(models.Model):
    text = models.TextField(
        verbose_name='Текст отзыва'
    )
    score = models.IntegerField(
        verbose_name='Оценка',
        blank=False,
        validators=(
            MinValueValidator(1),
            MaxValueValidator(10)
        )
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации отзыва',
        auto_now_add=True
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Автор отзыва'
    )
    title = models.ForeignKey(
        Titles,
        on_delete=models.CASCADE,
        related_name='reviews',
    )

    class Meta:
        unique_together = ('author', 'title')
        ordering = ['-pub_date']

    def __str__(self):
        return self.text[:10]


class Comments(models.Model):
    review = models.ForeignKey(
        Reviews,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='comments',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата добавления комментария',
        auto_now_add=True
    )
    text = models.TextField(
        verbose_name='Текст комментария',
    )

    class Meta:
        ordering = ['-pub_date']

    def __str__(self):
        return self.text[:10]
