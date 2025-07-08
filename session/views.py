from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import SessionMember, Session,Note
from django.contrib.auth.models import User
from .serializers import SessionMemberSerializer,SessionSerializer, NoteSerializer
from rest_framework.exceptions import NotFound

class SessionMemberAPIView(APIView):
    def get(self, request, *args, **kwargs):
        members = SessionMember.objects.all()
        serializer = SessionMemberSerializer(members, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        serializer = SessionMemberSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, *args, **kwargs):
        try:
            member = SessionMember.objects.get(id=kwargs['id'])
        except SessionMember.DoesNotExist:
            raise NotFound("SessionMember not found.")
        
        serializer = SessionMemberSerializer(member, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        try:
            member = SessionMember.objects.get(id=kwargs['id'])
        except SessionMember.DoesNotExist:
            raise NotFound("SessionMember not found.")
        
        member.delete()
        return Response({"detail": "SessionMember deleted successfully."}, status=status.HTTP_204_NO_CONTENT)






class SessionAPIView(APIView):
    def get(self, request, *args, **kwargs):
        sessions = Session.objects.all()
        serializer = SessionSerializer(sessions, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        serializer = SessionSerializer(data=request.data)
        if serializer.is_valid():
            session = serializer.save()
            return Response(SessionSerializer(session).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, *args, **kwargs):
        try:
            session = Session.objects.get(id=kwargs['id'])
        except Session.DoesNotExist:
            raise NotFound("Session not found.")
        
        serializer = SessionSerializer(session, data=request.data, partial=True)
        if serializer.is_valid():
            session = serializer.save()
            return Response(SessionSerializer(session).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        try:
            session = Session.objects.get(id=kwargs['id'])
        except Session.DoesNotExist:
            raise NotFound("Session not found.")
        
        session.delete()
        return Response({"detail": "Session deleted successfully."}, status=status.HTTP_204_NO_CONTENT)

class AddMemberAPIView(APIView):
    def post(self, request, *args, **kwargs):
        session_id = kwargs.get('session_id')
        user_id = request.data.get('user_id')
        permission = request.data.get('permission', {})

        try:
            session = Session.objects.get(id=session_id)
        except Session.DoesNotExist:
            raise NotFound("Session not found.")
        
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_400_BAD_REQUEST)

        member, created = SessionMember.objects.get_or_create(
            user=user, session=session, defaults={'permission': permission}
        )
        
        session.members.add(member)
        return Response({"detail": "Member added successfully."}, status=status.HTTP_200_OK)

class RemoveMemberAPIView(APIView):
    def post(self, request, *args, **kwargs):
        session_id = kwargs.get('session_id')
        user_id = request.data.get('user_id')

        try:
            session = Session.objects.get(id=session_id)
        except Session.DoesNotExist:
            raise NotFound("Session not found.")
        
        try:
            user = User.objects.get(id=user_id)
            member = session.members.get(user=user)
            session.members.remove(member)
            member.delete()
            return Response({"detail": "Member removed successfully."}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_400_BAD_REQUEST)
        except SessionMember.DoesNotExist:
            return Response({"detail": "Member is not part of the session."}, status=status.HTTP_400_BAD_REQUEST)
        






class NoteCreateAPIView(APIView):


    def post(self, request, *args, **kwargs):
        session_id = request.data.get('session')
        user = request.user  # Get the current logged-in user

        try:
            session = Session.objects.get(id=session_id)
        except Session.DoesNotExist:
            return Response({"error": "Session not found."}, status=status.HTTP_400_BAD_REQUEST)

        # Create new note
        note_data = request.data.copy()
        note_data['user'] = user.id
        note_data['session'] = session.id

        serializer = NoteSerializer(data=note_data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class NoteUpdateAPIView(APIView):

    def put(self, request, *args, **kwargs):
        note_id = kwargs.get('id')
        try:
            note = Note.objects.get(id=note_id, user=request.user)
        except Note.DoesNotExist:
            return Response({"error": "Note not found."}, status=status.HTTP_404_NOT_FOUND)

        # Update the note
        serializer = NoteSerializer(note, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class NoteDeleteAPIView(APIView):


    def delete(self, request, *args, **kwargs):
        note_id = kwargs.get('id')
        try:
            note = Note.objects.get(id=note_id, user=request.user)
        except Note.DoesNotExist:
            return Response({"error": "Note not found."}, status=status.HTTP_404_NOT_FOUND)

        note.delete()
        return Response({"message": "Note deleted successfully."}, status=status.HTTP_204_NO_CONTENT)

class NoteGetAPIView(APIView):


    def get(self, request, *args, **kwargs):
        note_id = kwargs.get('id')
        try:
            note = Note.objects.get(id=note_id, user=request.user)
        except Note.DoesNotExist:
            return Response({"error": "Note not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = NoteSerializer(note)
        return Response(serializer.data)

class NoteListAPIView(APIView):


    def get(self, request, *args, **kwargs):
        session_id = request.query_params.get('session')
        if not session_id:
            return Response({"error": "Session ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            session = Session.objects.get(id=session_id)
        except Session.DoesNotExist:
            return Response({"error": "Session not found."}, status=status.HTTP_400_BAD_REQUEST)

        notes = Note.objects.filter(session=session, user=request.user)
        serializer = NoteSerializer(notes, many=True)
        return Response(serializer.data)