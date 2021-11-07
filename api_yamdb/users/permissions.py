from rest_framework import permissions


class AdminOrOwnerDataAccess(permissions.BasePermission):

    def has_permission(self, request, view):
        # print (request.data['username'], request.user.username)
        if 'username' in request.resolver_match.kwargs:
            owner_data_flag = (
                    request.resolver_match.kwargs[
                        'username'] == request.user.username
                    or request.resolver_match.kwargs['username'] == 'me')
        else:
            owner_data_flag = False
        print("Owner data flag =", owner_data_flag)
        print(request.resolver_match.kwargs)
        return (
                request.user.is_staff
                or request.user.is_superuser
                or request.user.role == 'admin'
                or owner_data_flag
        )

    def has_object_permission(self, request, view, obj):
        return (
                obj.username == request.user.username
                or request.user.is_staff
                or request.user.is_superuser
                or request.user.role == 'admin'
        )
