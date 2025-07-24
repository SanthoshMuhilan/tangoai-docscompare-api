from fastapi import APIRouter
from app.services.openai_gpt import compare_documents

router = APIRouter()

@router.post("/")
async def compare(doc_ids: list):
    differences = await compare_documents(doc_ids)
    return {"differences": differences}