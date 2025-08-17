from rest_framework import permissions

class IsSellerUser(permissions.BasePermission):
    """
    Allows access only to users with seller role.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.user_type == 'SELLER')

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    Assumes the model instance has an `owner` attribute.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Instance must have an attribute named 'owner' or 'seller' or 'user'.
        if hasattr(obj, 'owner'):
            return obj.owner == request.user
        elif hasattr(obj, 'seller'):
            return obj.seller == request.user
        elif hasattr(obj, 'user'):
            return obj.user == request.user
            
        return False

class IsOwner(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to access it.
    """
    def has_object_permission(self, request, view, obj):
        # Instance must have an attribute named 'owner' or 'seller' or 'user'.
        if hasattr(obj, 'owner'):
            return obj.owner == request.user
        elif hasattr(obj, 'seller'):
            return obj.seller == request.user
        elif hasattr(obj, 'user'):
            return obj.user == request.user
            
        return False
