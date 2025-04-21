from sentence_transformers import SentenceTransformer, util
import logging

from django.http import JsonResponse
import logging
from sentence_transformers import SentenceTransformer, util
import torch



# Load the SentenceTransformer model
model = SentenceTransformer('all-MiniLM-L6-v2')

def generate_embedding_to_upload(text):
    try:
        # Generate the embedding for the provided text using the model
        embedding = model.encode(text).tolist()
        return embedding
    except Exception as e:
        logging.error(f"Error generating embedding: {e}")
        return None

def generate_embedding(text):
    try:
        embedding = model.encode(text)
        logging.info(f"Generated embedding for text: {text} - {embedding[:10]}...")  # Log first 10 elements of the embedding
        return embedding
    except Exception as e:
        logging.error(f"Error generating embedding: {e}")
        return None

def compute_similarity(embedding1, embedding2):
    try:
        # Ensure embeddings are tensors for proper computation
        embedding1_tensor = torch.tensor(embedding1)
        embedding2_tensor = torch.tensor(embedding2)
        cosine_similarity = util.pytorch_cos_sim(embedding1_tensor, embedding2_tensor)
        similarity_value = cosine_similarity.item()
        logging.info(f"Computed similarity: {similarity_value}")
        return similarity_value
    except Exception as e:
        logging.error(f"Error computing similarity: {e}")
        return None
    

# import openai

# # Initialize OpenAI API client
# openai.api_key = 'your_openai_api_key'

# # Define function to call LLM for generating a better answer
# def generate_llm_answer(query, page_text):
#     try:
#         # Use OpenAI's model to generate a more contextual answer
#         response = openai.Completion.create(
#             engine="text-davinci-003",  # You can change this to the model you prefer
#             prompt=f"Question: {query}\nDocument text: {page_text}\nProvide a relevant and clear answer based on the document text.",
#             max_tokens=150,
#             temperature=0.7
#         )
#         return response.choices[0].text.strip()
#     except Exception as e:
#         logging.error(f"Error while generating LLM answer: {e}")
#         return None
    



# import google.generativeai as gmini
# import logging
# import google.generativeai as genai

# # Configure Gmini API key
# gmini.configure(api_key="AIzaSyDV50bo1Gol6E16Gs04vLdZtJkLQBir4-I")
# genai.configure(api_key="AIzaSyDV50bo1Gol6E16Gs04vLdZtJkLQBir4-I")

# def generate_llm_answer(query, page_text):
#     try:
#         # Split the long text into smaller chunks (e.g., sentences or paragraphs)
#         chunks = chunk_text(page_text, max_chunk_size=1000)  # Adjust chunk size as needed
        
#         # Loop through each chunk and check for the best match
#         best_answer = None
#         for chunk in chunks:
#             prompt = (
#                 f"Based on the following text from a document:\n{chunk}\n\n"
#                 f"Answer the question: {query}\n"
#                 f"Provide a clear, concise, and accurate answer based on the provided text."
#             )

#             # Generate content using gmini.generate_text
#             response = gmini.generate_text(  # Assuming this is the method for generating text
#                 prompt=prompt,
#                 model="text-bison",  # Replace with the actual gmini model you're using
#                 temperature=0.7,
#                 max_output_tokens=300  # Adjust based on how detailed you want the response
#             )
            
#             # If an answer is found, use it and stop checking further chunks
#             if response.get('text'):  # Assuming the response is a dictionary with 'text' key
#                 best_answer = response['text'].strip()
#                 break  # Stop if we find a valid answer

#         # Return the best answer
#         return best_answer if best_answer else "No relevant answer found in the document."

#     except Exception as e:
#         logging.error(f"Error while generating LLM answer: {e}")
#         return None


# def chunk_text(text, max_chunk_size=1000):
#     """Helper function to chunk long text into smaller pieces."""
#     chunks = []
#     while len(text) > max_chunk_size:
#         chunk = text[:max_chunk_size]
#         chunks.append(chunk)
#         text = text[max_chunk_size:]
#     if text:
#         chunks.append(text)  # Add the final chunk
#     return chunks