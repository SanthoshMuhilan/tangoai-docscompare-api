from app.services.openai_gpt import create_embedding
from app.services.azure_cosmos import save_chunk
from typing import List

def chunk_text(text: str, chunk_size: int = 500):
   """Split text into smaller chunks"""
   if isinstance(text,list):
       text = " ".join(text)
   words = text.split()
   return [" ".join(words[i:i + chunk_size]) for i in range(0, len(words), chunk_size)]


def preprocess(document_id: str, full_text: str):
   # Preprocess: chunk and embed
   chunks = chunk_text(full_text)
   for idx, chunk in enumerate(chunks):
       embedding = create_embedding(chunk)
       save_chunk(document_id, idx, chunk, embedding)
   print(f"Preprocessed and saved {len(chunks)} chunks for {document_id}")