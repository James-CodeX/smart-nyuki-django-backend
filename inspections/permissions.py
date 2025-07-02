from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    Users can only view and modify their own inspection schedules and reports.
    """

    def has_permission(self, request, view):
        """
        Check if the user has permission to access the view.
        Only authenticated users with beekeeper profiles can access.
        """
        if not request.user.is_authenticated:
            return False
        
        # For creation, user must have a beekeeper profile
        if view.action == 'create':
            return hasattr(request.user, 'beekeeper_profile')
        
        return True

    def has_object_permission(self, request, view, obj):
        """
        Check if the user has permission to access the specific object.
        Users can only access their own inspection schedules/reports.
        """
        if not request.user.is_authenticated:
            return False
        
        if not hasattr(request.user, 'beekeeper_profile'):
            return False
        
        # For inspection schedules
        if hasattr(obj, 'hive'):
            return obj.hive.apiary.beekeeper == request.user.beekeeper_profile
        
        # For inspection reports
        if hasattr(obj, 'inspector'):
            # User can access their own reports or reports for their hives
            return (
                obj.inspector == request.user or 
                obj.hive.apiary.beekeeper == request.user.beekeeper_profile
            )
        
        return False


class IsInspectorOrHiveOwner(permissions.BasePermission):
    """
    Permission for inspection reports - allows access to the inspector
    who created the report or the owner of the hive.
    """

    def has_permission(self, request, view):
        """
        Check if the user has permission to access the view.
        """
        if not request.user.is_authenticated:
            return False
        
        return hasattr(request.user, 'beekeeper_profile')

    def has_object_permission(self, request, view, obj):
        """
        Check if the user has permission to access the specific inspection report.
        """
        if not request.user.is_authenticated:
            return False
        
        if not hasattr(request.user, 'beekeeper_profile'):
            return False
        
        # User can access if they are the inspector or the hive owner
        return (
            obj.inspector == request.user or
            obj.hive.apiary.beekeeper == request.user.beekeeper_profile
        )
