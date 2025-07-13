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
from session.models import Youtube, YoutubeSummery, Session,TextSummery,ImageSummery
from .serializers import YoutubeSerializer,YoutubeCreateSerializer,TextSummerySerializer
import openai


# from azure.ai.openai import OpenAIClient
# from azure.core.credentials import AzureKeyCredential
# from azure.ai.openai import AzureOpenAI
from openai import AzureOpenAI, Client


# # Initialize the summarizer model
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

def summarize_text(text):
    """
    Use a pre-trained summarization model to summarize the transcript or text.
    """
    # Check if the text is empty or too short
    if not text or len(text.strip()) < 5:
        return "Text is too short or empty to summarize."

    # Debugging output (optional, can be removed later)
    print(f"Input text length: {len(text)}")
    print(f"Input text preview: {text[:200]}...")  # Preview first 200 chars for debugging
    
    try:
        # Check if the text is too long, and break it into chunks if necessary
        if len(text.split()) > 1000:  # If the text exceeds 1000 words, break it into chunks
            text_chunks = [text[i:i+1000] for i in range(0, len(text), 1000)]
            summaries = []
            for chunk in text_chunks:
                chunk_summary = summarizer(chunk, max_length=200, min_length=50, do_sample=False)
                summaries.append(chunk_summary[0]['summary_text'])
            return " ".join(summaries)
        
        # If the text length is reasonable, summarize it directly
        summarized = summarizer(text, max_length=200, min_length=50, do_sample=False)
        
        # Ensure we have the result and it is properly structured
        if summarized and isinstance(summarized, list) and len(summarized) > 0:
            return summarized[0]['summary_text']
        else:
            return "Error: Summarizer returned an empty or invalid result."

    except Exception as e:
        return f"Error summarizing text: {str(e)}"


@api_view(['POST'])
def get_summary(request):
    text = request.data.get('text', None)
    session_id = request.data.get('session', None)  # Extract the session ID from the request
    
    # If text or session is not provided, return an error
    if not text:
        return Response({"error": "Text is required"}, status=400)
    if not session_id:
        return Response({"error": "Session is required"}, status=400)
    
    try:
        # Fetch the session using the session_id (ensure the session exists)
        session = Session.objects.get(id=session_id)
        
        # Summarize the provided text
        summary = summarize_text(text)

        # Assuming you want to save the summary for the logged-in user
        user = request.user  # Get the user from the request (ensure the user is authenticated)

        # Create and save the TextSummery instance
        text_summary = TextSummery(user=user, session=session, text=text, summery=summary)
        text_summary.save()

        # Return the summary in the response
        return Response({"summary": summary})
    
    except Session.DoesNotExist:
        return Response({"error": "Session not found"}, status=400)
    except Exception as e:
        return Response({"error": f"An error occurred: {str(e)}"}, status=500)
    


from django.shortcuts import get_object_or_404

class TextSummeryBySessionView(APIView):
    
    def get(self, request, *args, **kwargs):
        # Extract session_id from query parameters
        session_id = request.query_params.get('session_id', None)
        
        # If session_id is not provided, return an error
        if not session_id:
            return Response({'error': 'Session ID is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Fetch the session object using the session_id
            session = get_object_or_404(Session, id=session_id)
            
            # Retrieve all summaries associated with the session
            text_summaries = TextSummery.objects.filter(session=session)
            
            if not text_summaries.exists():
                return Response({'message': 'No summaries found for this session.'}, status=status.HTTP_200_OK)
            # Serialize the summaries
            serializer = TextSummerySerializer(text_summaries, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)



        except Session.DoesNotExist:
            return Response({'error': 'Session not found'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

###################################33



class YoutubeCreate(APIView):
    def post(self, request):
        user = request.user
        session_id = request.data.get('session')  # Get the session ID
        link = request.data.get('link')

        # Check if the link already exists for the session and user
        if Youtube.objects.filter(session_id=session_id, user=user, link=link).exists():
            return Response({"message": "This link already exists for this session and user."}, status=status.HTTP_400_BAD_REQUEST)

        # If not, create the Youtube object
        serializer = YoutubeCreateSerializer(data=request.data)
        if serializer.is_valid():
            # Get the actual Session instance
            session = Session.objects.get(id=session_id)
            serializer.save(user=user, session=session)  # Assign the session instance
            return Response(serializer.data, status=status.HTTP_201_CREATED)


class YoutubeList(APIView):
    def get(self, request):
        session= request.query_params.get('session', None)
        if session:
            try:
                session = Session.objects.get(id=session)
                youtubes = Youtube.objects.filter(session=session)
            except Session.DoesNotExist:
                return Response({"error": "Session not found."}, status=status.HTTP_404_NOT_FOUND)
        # youtubes = Youtube.objects.all()
        serializer = YoutubeCreateSerializer(youtubes, many=True)
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
    







from django.http import JsonResponse
from youtube_transcript_api import YouTubeTranscriptApi
import requests
import logging
import json
from django.shortcuts import render, reverse
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, JsonResponse
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

# Configure the API key
genai.configure(api_key="AIzaSyC4Mx6gYYvhY_Cm0FTCxOxmvfPP-p1agYU") 

def generate_summary(transcript_text, temp=0.001, max_output=1000, candidate_count=1):
    """
    This function generates a summary for the given transcript text.

    :param transcript_text: The text that needs to be summarized.
    :param temp: The temperature for text generation (controls randomness).
    :param max_output: The maximum number of tokens for the output.
    :param candidate_count: The number of candidate responses to generate.
    :return: The generated summary.
    """
    if not transcript_text:
        return "No transcript provided for summary."

    # Prepare the prompt for summarization
    prompt = f"""
    Please summarize the following transcript:

    Transcript:
    {transcript_text}

    Format:
    Provide a brief overview of the main points discussed in the transcript with details.
    """

    # Generate the response based on the prompt
    response = genai.GenerativeModel('gemini-2.5-flash').generate_content(
        [{'role': 'user', 'parts': [prompt]}],
        generation_config=genai.types.GenerationConfig(
            candidate_count=candidate_count,
            max_output_tokens=max_output,
            temperature=temp,
        ),
        safety_settings={
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE
        }
    )
    
    # Return the generated summary text
    return response.text

def index(request):
    transcript_text = ""
    summary = ""
    
    if request.method == 'POST':
        try:
            # Read and parse JSON data from the body
            data = json.loads(request.body.decode('utf-8'))
            
            # Extract video_url from the incoming JSON data
            video_url = data.get('video_url')
            
            if not video_url:
                return JsonResponse({'error': 'Video URL is required'}, status=400)
            
            # Extract video ID from YouTube URL
            if 'v=' in video_url:
                video_id = video_url.split('v=')[-1]
                # Handle cases with extra query parameters
                if '&' in video_id:
                    video_id = video_id.split('&')[0]
            else:
                return JsonResponse({'error': 'Invalid YouTube video URL'}, status=400)

            # Fetch transcript using the YouTubeTranscriptApi
            transcript = YouTubeTranscriptApi.get_transcript(video_id)
            transcript_text = ' '.join([entry['text'] for entry in transcript])
            
            # Generate summary for the transcript
            summary = generate_summary(transcript_text)
        
        except Exception as e:
            logging.error(f"Error occurred: {e}")
            return JsonResponse({'error': f"An error occurred: {str(e)}"}, status=500)
    
    return JsonResponse({'transcript_text': transcript_text, 'summary': summary})




###################################################

# image_extract/views.py
from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
import pytesseract
from PIL import Image
import io

import pytesseract
from PIL import Image
from django.http import JsonResponse
from rest_framework.decorators import api_view

# Ensure pytesseract knows where the Tesseract executable is located
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # Windows path
from accounts.models import User
@api_view(['POST'])
def extract_text_from_image(request):
    if 'image' not in request.FILES:
        return JsonResponse({'error': 'No image provided'}, status=400)

    # Get the image and title from the request
    image_file = request.FILES['image']
    title = request.data.get('title')  # Get the title from the request data
    # user = request.data.get('user') # Get the user from the request (assuming you're using authentication)
    user=request.user.id  # Get the user ID from the request
    session = request.data.get('session')  # Assuming session is provided in the request data
    
    if not session:
        return JsonResponse({'error': 'Session is required'}, status=400)
    
    if not title:
        return JsonResponse({'error': 'Title is required'}, status=400)

    try:
        # Open the image using PIL
        image = Image.open(image_file)

        # Use pytesseract to extract text
        extracted_text = pytesseract.image_to_string(image)
        session = Session.objects.get(id=session)  # Get the session object
        user=User.objects.get(id=user)  # Get the user object

        # Generate the summary of the extracted text
        summery = generate_summary(extracted_text)

        # Create a new ImageSummery instance and save it to the database
        image_summery = ImageSummery(
            user=user,
            session=session,
            title=title,  # Use the provided title
            image=image_file,
            summery=summery
        )
        image_summery.save()

        # Return the extracted text and summary as a response
        return JsonResponse({'extracted_text': extracted_text, 'summery': summery}, status=200)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    


@api_view(['GET'])
def get_images_by_session(request, session_id):
    try:
        # Retrieve all ImageSummery objects related to the session_id
        images = ImageSummery.objects.filter(session_id=session_id)

        # If no images are found, return an error message
        if not images.exists():
            return JsonResponse({'error': 'No images found for this session.'}, status=404)

        # Manually serialize the images into a list of dictionaries
        image_list = []
        for image in images:
            image_data = {
                'id': image.id,
                'title': image.title,
                'image_url': image.image.url,
                'summery': image.summery,
            }
            image_list.append(image_data)

        # Return the serialized data as a JSON response
        return JsonResponse({'images': image_list}, status=200)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@api_view(['DELETE'])
def delete_image_by_session(request, session_id, image_summery_id):
    try:
        # Find the ImageSummery object based on session_id and image_summery_id
        image_summery = ImageSummery.objects.filter(session_id=session_id, id=image_summery_id)

        # If no image is found, return an error message
        if not image_summery.exists():
            return JsonResponse({'error': 'No image found for the provided session_id and image_summery_id.'}, status=404)

        # Delete the image summary
        image_summery.delete()

        return JsonResponse({'message': 'Image summary has been deleted successfully.'}, status=200)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)