from django.urls import path
from . import views
from .views import YoutubeCreate, YoutubeList, YoutubeDetail ,TextSummeryBySessionView,index

urlpatterns = [
    path('summarize', views.get_summary, name='video_summary'),
    path('generate-summary_for_youtube', index, name='generate-summary'),
    path('get-text-summaries-by-session', TextSummeryBySessionView.as_view(), name='get_text_summaries_by_session'),


    path('youtube', YoutubeList.as_view(), name='youtube-list'),
    path('youtube/create', YoutubeCreate.as_view(), name='youtube-create'),
    path('youtube/<int:pk>', YoutubeDetail.as_view(), name='youtube-detail'),
]

