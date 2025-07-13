from django.urls import path
from . import views
from .views import YoutubeCreate, YoutubeList, YoutubeDetail,index,get_summary,TextSummeryBySessionView,extract_text_from_image,get_images_by_session,delete_image_by_session
from bot.views import SearchView
urlpatterns = [
    path('summarize', get_summary, name='video_summary'),
    path('generate-summary_for_youtube', index, name='generate-summary'),
    

    path('get-text-summaries-by-session', TextSummeryBySessionView.as_view(), name='get_text_summaries_by_session'),

    path('youtube', YoutubeList.as_view(), name='youtube-list'),
    path('youtube/create', YoutubeCreate.as_view(), name='youtube-create'),
    path('youtube/<int:pk>', YoutubeDetail.as_view(), name='youtube-detail'),

    path('extract-text-and-summery-image', extract_text_from_image, name='extract_text_from_image'),
    path('images/session/<int:session_id>', get_images_by_session, name='get_images_by_session'),
    path('images/session/<int:session_id>/delete/<int:image_summery_id>', delete_image_by_session, name='delete_image_by_session'),

    path('ask', SearchView.as_view(), name='search')
]

