from rest_framework import permissions


class IsAuthorOrStaffOrReadOnly(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        return (request.user.is_anonymous
                or request.user.role in ['admin', 'moderator']
                or request.method in permissions.SAFE_METHODS
                or obj.author == request.user)
