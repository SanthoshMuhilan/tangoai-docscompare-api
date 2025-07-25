# === semantic_search.py ===
from typing import List, Tuple
from app.services.azure_cosmos import save_file_metadata, fetch_chunks_by_document
from app.services.openai_gpt import create_embedding
import numpy as np

def cosine_similarity(vec1, vec2):
   """
   Calculate cosine similarity between two vectors
   """
   v1 = np.array(vec1)
   v2 = np.array(vec2)
   return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))

def semantic_search(document_id: str, query: str, top_k: int = 5):
   """
   Search for top_k most relevant chunks for a given query
   """
   # Fetch chunks + embeddings from Cosmos DB
   chunks, embeddings = fetch_chunks_by_document(document_id)
   # Create embedding for the user query
   query_embedding = create_embedding(query)
   # Score each chunk by similarity to the query
   scored_chunks = []
   for text, embed in zip(chunks, embeddings):
       score = cosine_similarity(query_embedding, embed)
       scored_chunks.append((text, score))
   # Sort by similarity score (descending)
   scored_chunks.sort(key=lambda x: x[1], reverse=True)
   # Return top_k results
   return scored_chunks[:top_k]