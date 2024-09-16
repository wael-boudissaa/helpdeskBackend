from rest_framework.permissions import BasePermission

class IsApplicant(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return hasattr(user, 'applicant')
class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return hasattr(user, 'admin')
class IsExpert(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return hasattr(user, 'expert')