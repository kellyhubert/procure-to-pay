from rest_framework import permissions


class IsStaff(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'staff'


class IsApprover(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role in ['approver-level-1', 'approver-level-2']


class IsFinance(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'finance'


class IsStaffOrFinance(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role in ['staff', 'finance']


class CanEditRequest(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.can_be_edited_by(request.user)


class CanApproveRequest(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False

        user_role = request.user.role
        if user_role not in ['approver-level-1', 'approver-level-2']:
            return False

        return obj.status == 'pending'
