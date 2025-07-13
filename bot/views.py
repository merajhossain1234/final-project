from django.http import JsonResponse
from django.views import View
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import AzureOpenAIEmbeddings, AzureChatOpenAI
from langchain_community.vectorstores import FAISS
import traceback
import json
import os
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from langchain.prompts.chat import ChatPromptTemplate
import re
from langchain.schema import Document

# Set your Azure OpenAI environment variables
os.environ["AZURE_OPENAI_API_KEY"] = "3b7a98b8533f4de1b62201f79804e573"
os.environ["AZURE_OPENAI_ENDPOINT"] = "https://aise.openai.azure.com/"
os.environ["AZURE_OPENAI_API_VERSION"] = "2024-02-15-preview"
os.environ["AZURE_OPENAI_CHAT_DEPLOYMENT_NAME"] = "gpt-35-turbo-16k"


# Define the class-based view
@method_decorator(csrf_exempt, name='dispatch')
class SearchView(View):
    
    def get_file_path(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(current_dir, "project.txt")
        return file_path

    def load_documents(self, file_path):
        loader = TextLoader(file_path, encoding='utf-8')
        try:
            documents = loader.load()
            # print(f"Loaded documents: {documents}")
        except Exception as e:
            print(f"Error loading file: {e}")
            traceback.print_exc()
            documents = []
        return documents

    def create_faiss_index(self, docs, embeddings):
        try:
            index = FAISS.from_documents(docs, embeddings)
            print("FAISS index created.")
        except Exception as e:
            print(f"Error creating FAISS index: {e}")
            traceback.print_exc()
            index = None
        return index

    def initialize_embeddings(self):
        try:
            embeddings = AzureOpenAIEmbeddings()
            print("Azure OpenAI Embeddings initialized.")
        except Exception as e:
            print(f"Error initializing Azure OpenAI Embeddings: {e}")
            traceback.print_exc()
            embeddings = None
        return embeddings

    def split_documents(self, documents):
        # Combine all documents into a single string
        full_text = "\n".join(documents)  # documents is already a list of strings

        try:
            # Regular expression to split on headings starting with "###"
            sections = re.split(r'(?m)^###\s+', full_text)
            # Remove any empty strings
            sections = [sec.strip() for sec in sections if sec.strip()]
            # Create Document objects for each section
            docs = [Document(page_content=sec) for sec in sections]
            print(f"Split documents into {len(docs)} sections based on headings.")
        except Exception as e:
            print(f"Error splitting documents: {e}")
            traceback.print_exc()
            docs = []
        return docs

    def initialize_index(self, text):
        if not text:
            print("No text provided for indexing.")
            return None
        documents = text.split("\n")
        if documents:
            embeddings = self.initialize_embeddings()
            if embeddings:
                docs = self.split_documents(documents)
                index = self.create_faiss_index(docs, embeddings)  
            else:
                index = None
                print("Embeddings initialization failed.")
        else:
            index = None
            print("No documents loaded. Please check the file path and content.")
        return index

    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body.decode('utf-8'))
            query = data.get('query', '')
            text = data.get('text', '')
            
            if not text:
                return JsonResponse({'error': 'Text is missing in the request.'}, status=400)

            index = self.initialize_index(text)
            if not index:
                return JsonResponse({'error': 'Index is not initialized.'}, status=500)

            # Perform the search
            try:
                results = index.similarity_search(query, k=3)  # Retrieve top 3 relevant sections
            except Exception as e:
                print(f"Error performing search: {e}")
                traceback.print_exc()  # Log the full stack trace
                return JsonResponse({'error': 'Error performing search.'}, status=500)

            # Check if there are relevant documents
            if not results:
                return JsonResponse({'question': query, 'response': 'No relevant information found.'})

            # Prepare messages
            try:
                api_version = os.environ.get("AZURE_OPENAI_API_VERSION")
                deployment_name = os.environ.get("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME")
                response = AzureChatOpenAI(
                    openai_api_version=api_version,
                    azure_deployment=deployment_name
                )

                system_message = {
                    "role": "system",
                    "content": (
                        "You are a professional AI assistant that provides answers **only** based on the given context. "
                        "You **must not** use any external information or prior knowledge. "
                        "If the information is not in the context, respond by saying: 'I'm sorry, but I don't have information on that topic. Feel free to ask about anything else, and I'll do my best to assist.' "
                    )
                }

                context_messages = []
                for idx, result in enumerate(results):
                    context_messages.append({
                        "role": "assistant",
                        "content": f"Context Section {idx+1}:\n{result.page_content}"
                    })

                user_message = {
                    "role": "user",
                    "content": query
                }

                messages = [system_message] + context_messages + [user_message]

                ai_msg = response.invoke(messages)
                generated_text = ai_msg.content.strip()
            except Exception as e:
                print(f"Error generating response: {e}")
                traceback.print_exc()  # Log the full stack trace
                return JsonResponse({'error': 'Error generating response.'}, status=500)

            return JsonResponse({'question': query, 'response': generated_text})

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON format in request body.'}, status=400)

        except Exception as e:
            print(f"Unhandled exception: {e}")
            traceback.print_exc()  # Log the full stack trace for debugging
            return JsonResponse({'error': 'Unhandled exception occurred.'}, status=500)
