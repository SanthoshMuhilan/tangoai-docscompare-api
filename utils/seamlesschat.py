# seamless_chat.py
from app.services.azure_cosmos import fetch_chat_history, save_chat_result , fetch_chunks_by_document
from app.services.openai_gpt import compare_documents
from app.services.openai_gpt import analyze_single_text
from datetime import datetime
# In-memory session cache (could be swapped with Redis later)
session_cache = {}
def start_chat_session(document_id: str) -> dict:
   """
   Start a chat session for the given document ID.
   Fetch chunks + previous chats and cache them for session continuity.
   """
   print(f" Starting chat session for Document ID: {document_id}")
   # Fetch document chunks
   chunks, document_name = fetch_chunks_by_document_id(document_id)
   if not chunks:
       raise ValueError(f"Document ID {document_id} not found or no chunks available.")
   # Fetch chat history
   history = fetch_chat_history(document_id, limit=50)
   # Store session info in memory
   session_cache[document_id] = {
       "documentName": document_name,
       "chunks": chunks,
       "history": history
   }
   return {
       "documentId": document_id,
       "documentName": document_name,
       "chatHistory": history
   }

def continue_chat_session(document_id: str, user_prompt: str, metadata: dict = None) -> dict:
   """
   Continue the chat session: handle user prompt, generate response, and save to DB.
   """
   print(f" Continuing chat session for Document ID: {document_id}")
   if document_id not in session_cache:
       raise ValueError("Session not found. Start session first.")
   # Retrieve session data
   session_data = session_cache[document_id]
   chunks = session_data["chunks"]
   history = session_data["history"]
   # Prepare context for GPT
   context_text = "\n".join(chunks)
   if history:
       history_text = "\n".join(
           [f"Q: {chat['userPrompt']}\nA: {chat['gptResponse']}" for chat in history]
       )
       context_text += f"\n\n--- Previous Conversation ---\n{history_text}"
   # Get GPT response
   gpt_response = analyze_single_text(context_text, user_prompt)
   # Build new chat entry
   new_chat = {
       "documentId": document_id,
       "documentName": session_data["documentName"],
       "userPrompt": user_prompt,
       "gptResponse": gpt_response,
       "createdAt": datetime.utcnow().isoformat(),
       "metadata": metadata or {}
   }
   chat_id = save_chat_result(new_chat)
   new_chat["chatId"] = chat_id
   # Update session cache
   session_data["history"].insert(0, new_chat)
   return {
       "chatId": chat_id,
       "response": gpt_response,
       "chatHistory": session_data["history"]
   }

   
def end_chat_session(document_id: str):
   """
   End the chat session and clear it from memory.
   """
   print(f"Ending chat session for Document ID: {document_id}")
   session_cache.pop(document_id, None)