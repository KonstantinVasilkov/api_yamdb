from django.shortcuts import get_object_or_404
from rest_framework import filters, viewsets
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.pagination import PageNumberPagination
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend

from reviews.models import Review, Title, Genre, Category
from .permissions import IsAuthorOrStaffOrReadOnly, IsAdminOrReadOnly

from .serializers import (CommentSerializer, ReviewSerializer,
                          TitleBaseSerializater, TitlePostSerializer,
                          GenreSerializer, CategorySerializer)


class GenreViewSet(viewsets.ModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'

    http_method_names = ['get', 'post', 'head', 'delete']

    def retrieve(self, request, slug):
        raise MethodNotAllowed("Не разрешенный метод")

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'

    # http_method_names = ['get', 'post', 'head', 'delete']

    # def retrieve(self, request, slug):
        # raise MethodNotAllowed("Не разрешенный метод")

class TitlesViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all()
    # pagination_class = LimitOffsetPagination
    pagination_class = PageNumberPagination

    permission_classes = (
        IsAdminOrReadOnly,
        # IsAuthorOrStaffOrReadOnly,
        # IsAuthenticatedOrReadOnly
    )
    filter_backends = (DjangoFilterBackend, filters.SearchFilter,
                       filters.OrderingFilter)
    filterset_fields = ('genre', 'category')
    ordering_fields = ('name',)
    ordering = ['name']

    def get_serializer_class(self):
        if self.request.method == ('get'):
            return TitlePostSerializer
        return TitleBaseSerializater


class ReviewsViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    pagination_class = LimitOffsetPagination
    permission_classes = (
        IsAuthorOrStaffOrReadOnly,
        IsAuthenticatedOrReadOnly
    )

    def _get_title(self):
        return get_object_or_404(Title, id=self.kwargs['title_id'])

    def perform_create(self, serializer):
        title = self._get_title()
        serializer.save(author=self.request.user, title=title)

    def get_queryset(self):
        title = self._get_title()
        return title.reviews.all()


class CommentsViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = CommentSerializer
    pagination_class = LimitOffsetPagination
    permission_classes = (
        IsAuthorOrStaffOrReadOnly,
        IsAuthenticatedOrReadOnly
    )

    def _get_review(self):
        return get_object_or_404(Review, id=self.kwargs['review_id'])

    def perform_create(self, serializer):
        review = self._get_review()
        serializer.save(author=self.request.user, review=review)

    def get_queryset(self):
        review = self._get_review()
        return review.comments.all()
