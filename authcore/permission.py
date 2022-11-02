from rest_framework import permissions


class IsUserUpdate(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        return obj == request.user


class IsUserChUpdate(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user