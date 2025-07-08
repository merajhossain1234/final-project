from rest_framework.response import Response
from rest_framework.decorators import api_view
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter
from transformers import pipeline
import requests
import re
import speech_recognition as sr
from pydub import AudioSegment
from io import BytesIO



from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from session.models import Youtube, YoutubeSummery
from .serializers import YoutubeSerializer

# Initialize the summarizer model
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

@api_view(['POST'])
def get_summary(request):
    video_url = request.data.get('video_url', None)
    audio_url = request.data.get('audio_url', None)
    text = request.data.get('text', None)
    
    if not any([video_url, audio_url, text]):
        return Response({"error": "Provide either video_url, audio_url, or text for summarization."}, status=400)
    
    # Process Video URL (YouTube)
    if video_url:
        # Extract YouTube video ID from URL
        video_id = extract_youtube_video_id(video_url)
        if not video_id:
            return Response({"error": "Invalid YouTube URL"}, status=400)

        try:
            youtube = Youtube.objects.get(link=video_url)
        
            # Check if the summary already exists for this YouTube video
            summary_exists = YoutubeSummery.objects.filter(youtube=youtube).first()
            if summary_exists:
                # If summary exists, return the existing summary
                return Response({"summary": summary_exists.summary})

            # If no summary exists, proceed to fetch the transcript and generate a summary
            transcript = YouTubeTranscriptApi.get_transcript(video_id)
            text = "\n".join([item['text'] for item in transcript])
            
            # Generate the summary using the extracted text
            summary = summarize_text(text)

            # Save the summary for future use
            YoutubeSummery.objects.create(youtube=youtube, summary=summary)

            return Response({"summary": summary})

        except Exception as e:
            return Response({"error": f"Error fetching transcript: {str(e)}"}, status=500)

    # Process Audio URL
    elif audio_url:
        try:
            audio_text = extract_audio_text(audio_url)
            summary = summarize_text(audio_text)
            return Response({"summary": summary})
        except Exception as e:
            return Response({"error": f"Error processing audio: {str(e)}"}, status=500)

    # If text is provided directly
    if text:
        summary = summarize_text(text)
        return Response({"summary": summary})

def extract_youtube_video_id(url):
    """
    Extracts YouTube video ID from a YouTube URL.
    """
    video_id_match = re.search(r"(?:youtu\.be/|youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*\?v=))([^""&?\/\s]+)", url)
    return video_id_match.group(1) if video_id_match else None

def extract_audio_text(audio_url):
    """
    Extracts text from an audio file (MP3, WAV) using speech recognition.
    """
    try:
        # Download the audio file from the URL
        response = requests.get(audio_url)
        audio = AudioSegment.from_mp3(BytesIO(response.content))  # Convert MP3 to WAV
        audio_path = "/tmp/temp_audio.wav"
        audio.export(audio_path, format="wav")  # Export to a temporary WAV file
        
        # Perform speech recognition
        recognizer = sr.Recognizer()
        with sr.AudioFile(audio_path) as source:
            audio_data = recognizer.record(source)
            text = recognizer.recognize_google(audio_data)
        
        return text

    except Exception as e:
        raise Exception(f"Error processing audio: {str(e)}")
    
def summarize_text(text):
    """
    Use a pre-trained summarization model to summarize the transcript or text.
    """
    try:
        summarized = summarizer(text, max_length=200, min_length=50, do_sample=False)
        return summarized[0]['summary_text']
    except Exception as e:
        return f"Error summarizing text: {str(e)}"

# from rest_framework.response import Response
# from rest_framework.decorators import api_view
# from youtube_transcript_api import YouTubeTranscriptApi
# from youtube_transcript_api.formatters import TextFormatter
# from transformers import pipeline
# import requests
# import re
# import speech_recognition as sr
# from pydub import AudioSegment
# from io import BytesIO

# # Summarizer initialization
# summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

# @api_view(['POST'])
# def get_summary(request):
#     video_url = request.data.get('video_url', None)
#     audio_url = request.data.get('audio_url', None)
#     text = request.data.get('text', None)
    
#     if not any([video_url, audio_url, text]):
#         return Response({"error": "Provide either video_url, audio_url, or text for summarization."}, status=400)
    
#     # Process Video URL (YouTube)
#     if video_url:
#         # Extract YouTube video ID from URL
#         video_id = extract_youtube_video_id(video_url)
#         if not video_id:
#             return Response({"error": "Invalid YouTube URL"}, status=400)

#         try:

#             transcript = YouTubeTranscriptApi.get_transcript(video_id)
#             text = "\n".join([item['text'] for item in transcript])
#         except Exception as e:
#             return Response({"error": f"Error fetching transcript: {str(e)}"}, status=500)

#     # Process Audio URL
#     elif audio_url:
#         try:
#             audio_text = extract_audio_text(audio_url)
#             text = audio_text
#         except Exception as e:
#             return Response({"error": f"Error processing audio: {str(e)}"}, status=500)

#     # If text is provided directly
#     if text:
#         summary = summarize_text(text)
#         return Response({"summary": summary})

# def extract_youtube_video_id(url):
#     """
#     Extracts YouTube video ID from a YouTube URL.
#     """
#     video_id_match = re.search(r"(?:youtu\.be/|youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*\?v=))([^""&?\/\s]+)", url)
#     return video_id_match.group(1) if video_id_match else None

# def extract_audio_text(audio_url):
#     """
#     Extracts text from an audio file (MP3, WAV) using speech recognition.
#     """
#     try:
#         # Download the audio file from the URL
#         response = requests.get(audio_url)
#         audio = AudioSegment.from_mp3(BytesIO(response.content))  # Convert MP3 to WAV
#         audio_path = "/tmp/temp_audio.wav"
#         audio.export(audio_path, format="wav")  # Export to a temporary WAV file
        
#         # Perform speech recognition
#         recognizer = sr.Recognizer()
#         with sr.AudioFile(audio_path) as source:
#             audio_data = recognizer.record(source)
#             text = recognizer.recognize_google(audio_data)
        
#         return text

#     except Exception as e:
#         raise Exception(f"Error processing audio: {str(e)}")
    
# def summarize_text(text):
#     """
#     Use a pre-trained summarization model to summarize the transcript or text.
#     """
#     try:
#         summarized = summarizer(text, max_length=200, min_length=50, do_sample=False)
#         return summarized[0]['summary_text']
#     except Exception as e:
#         return f"Error summarizing text: {str(e)}"




###################################33



class YoutubeCreate(APIView):
    def post(self, request):
        user = request.user
        session = request.data.get('session')
        link = request.data.get('link')

        # Check if the link already exists for the session and user
        if Youtube.objects.filter(session=session, user=user, link=link).exists():
            return Response({"message": "This link already exists for this session and user."}, status=status.HTTP_400_BAD_REQUEST)

        # If not, create the Youtube object
        serializer = YoutubeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=user, session=session)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class YoutubeList(APIView):
    def get(self, request):
        youtubes = Youtube.objects.all()
        serializer = YoutubeSerializer(youtubes, many=True)
        return Response(serializer.data)


class YoutubeDetail(APIView):
    def get(self, request, pk):
        try:
            youtube = Youtube.objects.get(pk=pk)
        except Youtube.DoesNotExist:
            return Response({"message": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = YoutubeSerializer(youtube)
        return Response(serializer.data)

    def put(self, request, pk):
        try:
            youtube = Youtube.objects.get(pk=pk)
        except Youtube.DoesNotExist:
            return Response({"message": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = YoutubeSerializer(youtube, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            youtube = Youtube.objects.get(pk=pk)
        except Youtube.DoesNotExist:
            return Response({"message": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        youtube.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)