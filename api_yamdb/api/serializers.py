from django.contrib.auth.models import AnonymousUser
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


class TitleSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = models.Title
