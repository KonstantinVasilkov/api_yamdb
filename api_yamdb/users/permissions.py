from rest_framework import permissions


class AdminOrOwnProfile(permissions.BasePermission):

    def has_permission(self, request, view):
        if 'username' in request.resolver_match.kwargs:
            own_data_flag = request.resolver_match.kwargs['username'] == 'me'
        else:
            own_data_flag = False
        if not request.user.is_authenticated:
            return False
        return (
                request.user.is_staff
                or request.user.is_superuser
                or request.user.role == 'admin'
                or own_data_flag
        )

    def has_object_permission(self, request, view, obj):
        return (
                obj.username == request.user.username
                or request.user.is_staff
                or request.user.is_superuser
                or request.user.role == 'admin'
        )
