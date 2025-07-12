from django.contrib import admin
from .models import (SessionMember,Session,Document,Youtube,YoutubeSummery,TextSummery,KnowledgeBase,Message, MemoryKnowledge, Note
)

# Registering each model for admin panel
@admin.register(SessionMember)
class SessionMemberAdmin(admin.ModelAdmin):
    list_display = ['user', 'permission']
    search_fields = ['user__email']

@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ['creator','session_name']
    search_fields = ['creator__email']
    filter_horizontal = ['members']  

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ['title', 'type', 'session', 'user']
    search_fields = ['title', 'user__email']
    list_filter = ['type']

@admin.register(Youtube)
class YoutubeAdmin(admin.ModelAdmin):
    list_display = ['title', 'type', 'link', 'session', 'user']
    search_fields = ['title', 'link', 'user__email']
    list_filter = ['type']

@admin.register(YoutubeSummery)
class YoutubeSummeryAdmin(admin.ModelAdmin):
    list_display = ['youtube', 'summery']
    search_fields = ['youtube__title']

@admin.register(KnowledgeBase)
class KnowledgeBaseAdmin(admin.ModelAdmin):
    list_display = ['object_id', 'type', 'page_no', 'session']
    search_fields = ['object_id', 'type']

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['question', 'answer', 'session', 'user']
    search_fields = ['question', 'user__email']

@admin.register(MemoryKnowledge)
class MemoryKnowledgeAdmin(admin.ModelAdmin):
    list_display = ['message']
    search_fields = ['message__question']

@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ['title', 'session', 'user']
    search_fields = ['title', 'user__email']
@admin.register(TextSummery)
class TextSummeryAdmin(admin.ModelAdmin):
    list_display = ['text', 'summery', 'session', 'user']
