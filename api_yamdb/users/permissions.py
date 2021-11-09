from rest_framework import permissions


class AdminOrOwnProfile(permissions.BasePermission):

    def has_permission(self, request, view):
        # print ("GENERAL PERMISSION")
        # print ("request: ", request)
        # print ("resolver_match: ", request.resolver_match)
        # print ("kwargs: ", request.resolver_match.kwargs)
        # print ("username: ", request.user.username)
        if 'username' in request.resolver_match.kwargs:
            own_data_flag = request.resolver_match.kwargs['username'] == 'me'
            # own_data_flag = request.resolver_match.kwargs['username'] == request.user.username
        else:
            own_data_flag = False
        # print ("own_data_flag: ", own_data_flag)

        if not request.user.is_authenticated:
            return False
        return (
                request.user.is_staff
                or request.user.is_superuser
                or request.user.role == 'admin'
                or own_data_flag
        )

    def has_object_permission(self, request, view, obj):
        print("OBJECT PERMISSION")
        print ("obj.usrename:", obj.username)
        return (
                obj.username == request.user.username
                # obj.username == 'me'
                # request.user.username == 'me'
                or request.user.is_staff
                or request.user.is_superuser
                or request.user.role == 'admin'
        )
