from django.shortcuts import get_object_or_404
from rest_framework import filters, viewsets
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from reviews.models import Comment, Review, Title
from .permissions import IsAuthorOrStaffOrReadOnly

from .serializers import CommentSerializer, ReviewSerializer, TitleSerializer


class TitlesViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all()
    serializer_class = TitleSerializer
    pagination_class = LimitOffsetPagination
    permission_classes = (
        IsAuthorOrStaffOrReadOnly,
        IsAuthenticatedOrReadOnly
    )


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
