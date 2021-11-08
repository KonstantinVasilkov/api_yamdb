from django.shortcuts import get_object_or_404
from rest_framework import filters, mixins, viewsets
from rest_framework.pagination import LimitOffsetPagination

from reviews.models import Comments, Reviews, Titles

from .serializers import CommentSerializer, ReviewSerializer, TitleSerializer


class TitlesViewSet(viewsets.ModelViewSet):
    queryset = Titles.objects.all()
    serializer_class = TitleSerializer
    pagination_class = LimitOffsetPagination


class ReviewsViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    pagination_class = LimitOffsetPagination
    # filter_backends = (filters.SearchFilter,)
    # search_fields = ('=category__', '=following__username')

    def _get_title(self):
        return get_object_or_404(Titles, id=self.kwargs['title_id'])

    def perform_create(self, serializer):
        title = self._get_title()
        serializer.save(author=self.request.user, title=title)

    def get_queryset(self):
        title = self._get_title()
        return title.reviews.all()


class CommentsViewSet(viewsets.ModelViewSet):
    queryset = Reviews.objects.all()
    serializer_class = CommentSerializer
    pagination_class = LimitOffsetPagination

    def _get_review(self):
        return get_object_or_404(Reviews, id=self.kwargs['review_id'])

    def perform_create(self, serializer):
        review = self._get_review()
        serializer.save(author=self.request.user, review=review)

    def get_queryset(self):
        review = self._get_review()
        return review.comments.all()
