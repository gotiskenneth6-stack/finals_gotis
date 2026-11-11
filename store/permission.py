
from rest_framework.permissions import BasePermission, SAFE_METHODS


# Admin can edit, add, and delete.
# Other authenticated users can only view.
class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        if request.method in SAFE_METHODS:
            return True

        return request.user.is_staff or request.user.is_superuser


# Admin can access everything.
# Users can only access their own Cart and Transactions.
class IsAdminOrOwner(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        if request.user.is_staff or request.user.is_superuser:
            return True

        owner = getattr(obj, "owner", None)
        buyer = getattr(obj, "buyer", None)

        return owner == request.user or buyer == request.user


# Admin can access all profiles.
# Users can only access their own profile.
class IsAdminOrProfileOwner(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        if request.user.is_staff or request.user.is_superuser:
            return True

        return obj == request.user
