from rest_framework import permissions

class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and 
            (request.user.role == 'admin' or request.user.is_superuser)
        )

'''class IsAdminOrTeacher(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and 
            (request.user.role in ['admin', 'teacher'] or request.user.is_superuser)
        )'''

class IsAdminOrTeacherReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        if request.user.role == 'admin' or request.user.is_superuser:
            return True
        if request.user.role == 'teacher' and request.method in permissions.SAFE_METHODS:
            return True
        return False