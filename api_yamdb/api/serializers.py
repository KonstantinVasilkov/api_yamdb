import datetime as dt

from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from reviews import models


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(slug_field='username',
                                          read_only=True)

    class Meta:
        model = models.Comment
        fields = ('id', 'text', 'author', 'pub_date')
        read_only_fields = ('review', 'author')


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(slug_field='username',
                                          read_only=True)

    class Meta:
        fields = ('id', 'text', 'author', 'score', 'pub_date')
        read_only_fields = ('author', 'title')
        model = models.Review

    def validate(self, data):
        title_id = self.context['view'].kwargs.get('title_id')
        request = self.context['request']
        title = get_object_or_404(models.Title, pk=title_id)
        if request.method == 'POST':
            if models.Review.objects.filter(
                    title=title,
                    author=request.user
            ).exists():
                raise ValidationError('Каждый пользователь может добавить не '
                                      'более одного ревью для каждого '
                                      'произведения!')
        return data


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Category
        fields = ('name', 'slug')


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Genre
        fields = ('name', 'slug')


class TitleBaseSerializater(serializers.ModelSerializer):
    genre = GenreSerializer(read_only=True, many=True)
    category = CategorySerializer(read_only=True)
    rating = serializers.SerializerMethodField()

    class Meta:
        model = models.Title
        fields = ('id', 'name', 'year', 'rating',
                  'description', 'genre', 'category')

    def get_rating(self, obj):
        score = 0
        reviews = obj.reviews.all()
        if not reviews:
            return None
        for review in reviews:
            score += review.score
        try:
            rating = round(score / reviews.count())
        except ZeroDivisionError:
            return None
        return rating


class TitlePostSerializer(serializers.ModelSerializer):
    genre = serializers.SlugRelatedField(many=True, slug_field='slug',
                                         queryset=models.Genre.objects.all())
    category = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=models.Category.objects.all()
    )

    class Meta:
        model = models.Title
        fields = ('id', 'name', 'year', 'description', 'genre', 'category')

    def validate_year(self, value):
        year = dt.date.today().year
        if 0 < value > year:
            raise serializers.ValidationError('Неправильный год!')
        return value
