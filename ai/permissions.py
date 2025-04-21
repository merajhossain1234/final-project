
from rest_framework import permissions
from session.models import Session, SessionMember
from django.contrib.auth.models import User

class IsMemberOfSession(permissions.BasePermission):
    """
    Custom permission to check if the user is part of the session.
    """

    def has_permission(self, request, view):
        try:
            # Get the session for the current user
            session = SessionMember.objects.get(user=request.user)
            
            # Check if the user is a member of the session
            if session:
                return True
            else:
                return False
        except SessionMember.DoesNotExist:
            return False