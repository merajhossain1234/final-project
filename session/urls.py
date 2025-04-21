from django.contrib import admin
from django.urls import path,include
from .views import SessionAPIView, AddMemberAPIView, RemoveMemberAPIView, SessionMemberAPIView

urlpatterns = [
    path('sessions', SessionAPIView.as_view(), name='session-list'),
    path('sessions/<int:id>', SessionAPIView.as_view(), name='session-detail'),
    path('sessions/add_member/<int:session_id>', AddMemberAPIView.as_view(), name='session-add-member'),
    path('sessions/remove_member/<int:session_id>', RemoveMemberAPIView.as_view(), name='session-remove-member'),
    path('session-members', SessionMemberAPIView.as_view(), name='sessionmember-list'),
    path('session-members/<int:id>', SessionMemberAPIView.as_view(), name='sessionmember-detail'),
]
