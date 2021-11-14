from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from users.models import User


class Category(models.Model):
    name = models.CharField(
        max_length=30,
        blank=False, verbose_name='Категория'
    )
    slug = models.SlugField(
        unique=True,
        blank=False, verbose_name='Адрес'
    )

    class Meta:
        verbose_name = 'category'

    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.CharField(
        max_length=30,
        blank=False, verbose_name='Жанр'
    )
    slug = models.SlugField(
        unique=True,
        blank=False, verbose_name='Адрес'
    )

    class Meta:
        verbose_name = 'genre'

    def __str__(self):
        return self.name


class Title(models.Model):
    name = models.CharField(
        max_length=50,
        verbose_name="Произведение",
        # unique=True
    )
    year = models.IntegerField(
        verbose_name="Дата выхода",
    )
    description = models.TextField(
        blank=True,
        verbose_name="Описание",
    )
    genre = models.ManyToManyField(
        Genre, through='GenreTitle')
    category = models.ForeignKey(
        Category,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="titles",
        verbose_name="Категория"
    )

    def __str__(self):
        return self.name


class Review(models.Model):
    text = models.TextField(
        verbose_name='Текст отзыва'
    )
    score = models.IntegerField(
        verbose_name='Оценка',
        validators=(
            MinValueValidator(
                1,
                message='Оценка должна быть в диапазоне от 1 до 10'
            ),
            MaxValueValidator(
                10,
                message='Оценка должна быть в диапазоне от 1 до 10'
            )
        )
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации отзыва',
        auto_now_add=True,
        db_index=True
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Автор отзыва',
        db_index=True
    )
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews',
    )

    class Meta:
        ordering = ['-pub_date']
        constraints = [
            models.UniqueConstraint(
                fields=('author', 'title'),
                name='one_review_per_title'
            ),
        ]
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'

    def __str__(self):
        return self.text[:10]


class Comment(models.Model):
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='comments',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        db_index=True
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата добавления комментария',
        auto_now_add=True,
        db_index=True
    )
    text = models.TextField(
        verbose_name='Текст комментария',
    )

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'Комментарий к отзыву'
        verbose_name_plural = 'Комментарии к отзыву'

    def __str__(self):
        return self.text[:10]


class GenreTitle(models.Model):
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)
    title = models.ForeignKey(Title, on_delete=models.CASCADE)
