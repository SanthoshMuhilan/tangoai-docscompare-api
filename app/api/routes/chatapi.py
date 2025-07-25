from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from app.utils.seamlesschat import start_chat_session, continue_chat_session, end_chat_session
app = FastAPI()
class ChatRequest(BaseModel):
   documentId: str
   userPrompt: str = None
   metadata: dict = None
@app.post("/start_session")
def start_session(request: ChatRequest):
   try:
       session_data = start_chat_session(request.documentId)
       return {"status": "success", "data": session_data}
   except Exception as e:
       raise HTTPException(status_code=400, detail=str(e))
@app.post("/continue_session")
def continue_session(request: ChatRequest):
   try:
       chat_data = continue_chat_session(
           request.documentId,
           request.userPrompt,
           request.metadata
       )
       return {"status": "success", "data": chat_data}
   except Exception as e:
       raise HTTPException(status_code=400, detail=str(e))
@app.post("/end_session")
def end_session(request: ChatRequest):
   try:
       end_chat_session(request.documentId)
       return {"status": "success", "message": "Session ended"}
   except Exception as e:
       raise HTTPException(status_code=400, detail=str(e))