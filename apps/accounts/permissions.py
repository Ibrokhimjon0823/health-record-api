from rest_framework import permissions

from .models import Role


class IsDoctor(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == Role.DOCTOR
        )


class IsPatient(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == Role.PATIENT
        )


class NoProfileSet(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.profile is None


class IsProfileSet(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.profile is not None
