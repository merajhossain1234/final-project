# my_app/views.py
import os
import google.generativeai as gmini
from django.http import JsonResponse
from django.views import View
from .embedding_service import generate_embedding, compute_similarity,generate_embedding_to_upload
from session.models import Document,Youtube, KnowledgeBase,Session,SessionMember
import fitz
from django.views.decorators.csrf import csrf_exempt
from .permissions import IsMemberOfSession
from rest_framework.permissions import IsAuthenticated  # Optional, if you need auth check as well
from rest_framework.decorators import permission_classes
import json
import logging
from django.http import JsonResponse
import io
import tempfile
from django.core.files.base import ContentFile

class PDFUploadView(View):

    def post(self, request, session_id):  # Accept session_id from URL
        try:
            if 'pdf_file' not in request.FILES:
                return JsonResponse({'error': 'No file provided.'}, status=400)

            # Get the uploaded file from request.FILES
            file = request.FILES['pdf_file']

            # Get the title from the POST data
            title = request.POST.get('title', 'Untitled') 

            # Check if the file is a PDF
            if not file.name.endswith(".pdf"):
                return JsonResponse({'error': 'Only PDF files are allowed.'}, status=400)

            # Try to fetch the session using session_id from the URL
            try:
                session = Session.objects.get(id=session_id)
            except Session.DoesNotExist:
                return JsonResponse({'error': 'Session not found.'}, status=404)

            # Save the uploaded file with a proper filename
            temp_file = tempfile.NamedTemporaryFile(delete=False, mode='wb')
            temp_file.write(file.read())  # Write the content to the temporary file
            temp_file.close()

            # Create the document record only if session is found
            if session:
                # Open the file again for saving it as ContentFile to the Document model
                with open(temp_file.name, 'rb') as temp_file:
                    doc_file = ContentFile(temp_file.read(), name=file.name)

                pdf_document = Document.objects.create(
                    type="pdf",
                    title=title,
                    pdf_file=doc_file,  # Save the PDF content as a file
                    session=session, 
                    user=None  # No user assigned since no authentication is used
                )

                # Open the PDF from the uploaded file using fitz (PyMuPDF)
                with fitz.open(temp_file.name) as pdf:
                    for page_num in range(len(pdf)):
                        page = pdf.load_page(page_num)
                        text = page.get_text("text")

                        # Generate embedding for the page text
                        embedding =generate_embedding_to_upload(text)

                        if embedding is None:
                            return JsonResponse({'error': 'Error generating embedding.'}, status=500)

                        # Save each page with text and embedding in the KnowledgeBase
                        knowledge_base_entry, created = KnowledgeBase.objects.update_or_create(
                            object_id=pdf_document.id,
                            page_no=page_num + 1,
                            defaults={
                                'type': pdf_document.type,
                                'text': text,
                                'vector': embedding,
                                'session': session
                            })

                return JsonResponse({'message': 'PDF uploaded and processed successfully'})
            else:
                return JsonResponse({'error': 'Session could not be found or is invalid.'}, status=404)

        except Exception as e:
            logging.error(f"Error in PDF upload view: {e}")
            return JsonResponse({'error': str(e)}, status=500)


#its wprking good

class PDFQueryView(View):
    def post(self, request, document_id):
        try:
            # Try to parse the JSON body
            try:
                data = json.loads(request.body)
                question = data.get('question')
            except json.JSONDecodeError:
                return JsonResponse({'error': 'Invalid JSON in the request.'}, status=400)

            if not question:
                return JsonResponse({'error': 'Question is missing in the request.'}, status=400)

            # Generate embedding for the user's query
            query_embedding = generate_embedding(question)
            if query_embedding is None:
                return JsonResponse({'error': 'Failed to generate embedding for the query.'}, status=500)

            # Retrieve all the pages for the document from the KnowledgeBase
            pages = KnowledgeBase.objects.filter(object_id=document_id).order_by('page_no')
            if not pages.exists():
                return JsonResponse({'error': 'No pages found for the given document.'}, status=404)

            # Process pages sequentially and return the first relevant one
            similarity_threshold = 0.1  # Temporarily set a lower threshold for debugging
            for page in pages:
                page_embedding = page.vector  # Retrieve stored embedding directly
                logging.info(f"Page {page.page_no} embedding: {page_embedding[:10]}...")  # Log first 10 elements of the embedding
                if page_embedding is None:
                    continue

                page_similarity = compute_similarity(query_embedding, page_embedding)
                logging.info(f"Similarity between query and page {page.page_no}: {page_similarity}")

                # Check if the similarity is above the threshold
                if page_similarity and page_similarity >= similarity_threshold:
                    # Return the first relevant page
                    return JsonResponse({'page': page.page_no, 'answer': page.text})

            logging.info("No relevant pages found.")
            return JsonResponse({'answer': 'No relevant pages found.'})

        except Exception as e:
            logging.error(f"An error occurred: {e}")
            return JsonResponse({'error': 'Internal server error'}, status=500)




# ## llm answer

# class PDFQueryView(View):
#     def post(self, request, document_id):
#         try:
#             # Try to parse the JSON body
#             try:
#                 data = json.loads(request.body)
#                 question = data.get('question')
#             except json.JSONDecodeError:
#                 return JsonResponse({'error': 'Invalid JSON in the request.'}, status=400)

#             if not question:
#                 return JsonResponse({'error': 'Question is missing in the request.'}, status=400)

#             # Generate embedding for the user's query
#             query_embedding = generate_embedding(question)
#             if query_embedding is None:
#                 return JsonResponse({'error': 'Failed to generate embedding for the query.'}, status=500)

#             # Retrieve all the pages for the document from the KnowledgeBase
#             pages = KnowledgeBase.objects.filter(object_id=document_id).order_by('page_no')
#             if not pages.exists():
#                 return JsonResponse({'error': 'No pages found for the given document.'}, status=404)

#             # Process pages sequentially and return the first relevant one
#             similarity_threshold = 0.1  # Temporarily set a lower threshold for debugging
#             for page in pages:
#                 page_embedding = page.vector  # Retrieve stored embedding directly
#                 logging.info(f"Page {page.page_no} embedding: {page_embedding[:10]}...")  # Log first 10 elements of the embedding
#                 if page_embedding is None:
#                     continue

#                 page_similarity = compute_similarity(query_embedding, page_embedding)
#                 logging.info(f"Similarity between query and page {page.page_no}: {page_similarity}")

#                 # Check if the similarity is above the threshold
#                 if page_similarity and page_similarity >= similarity_threshold:
#                     # Generate a better answer using LLM
#                     answer = generate_llm_answer(question, page.text)
#                     if answer:
#                         return JsonResponse({'page': page.page_no, 'answer': answer})

#             logging.info("No relevant pages found.")
#             return JsonResponse({'answer': 'No relevant pages found.'})

#         except Exception as e:
#             logging.error(f"An error occurred: {e}")
#             return JsonResponse({'error': 'Internal server error'}, status=500)