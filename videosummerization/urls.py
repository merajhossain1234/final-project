from django.urls import path
from . import views
from .views import YoutubeCreate, YoutubeList, YoutubeDetail

urlpatterns = [
    path('summarize', views.get_summary, name='video_summary'),

    path('youtube', YoutubeList.as_view(), name='youtube-list'),
    path('youtube/create', YoutubeCreate.as_view(), name='youtube-create'),
    path('youtube/<int:pk>', YoutubeDetail.as_view(), name='youtube-detail'),
]

