# === compare.py ===
from fastapi import APIRouter
from app.services.azure_cosmos import save_comparison_result, fetch_chunks_by_document
from app.services.openai_gpt import compare_texts
from app.utils.semanticsearch import semantic_search
from app.utils.chunkingpreprocess import preprocess
from datetime import datetime

router = APIRouter()


@router.get("/comparedocs")
def comparetwodocs(doc_id_1: str, doc_id_2: str, doc_id_1_fullText: str, doc_id_2_fullText: str, prompt: str) -> str:
   preprocess(doc_id_1, doc_id_1_fullText)
   preprocess(doc_id_2, doc_id_2_fullText)
   print(f"Fetching chunks for documents: {doc_id_1}, {doc_id_2}")

   semantic_search_results_1 = semantic_search(doc_id_1, prompt)
   semantic_search_results_2 = semantic_search(doc_id_2, prompt)
   print("Sending both documents to GPT for comparison...")

   comparison_summary = compare_texts(semantic_search_results_1, semantic_search_results_2, prompt)
   print("Comparison completed. Saving results...")
      
   return {"comparison_summary": comparison_summary}   

@router.get("/comparedocsdirect")
def comparetwodocsdirect(doc_id_1: str, doc_id_2: str, doc_id_1_fullText: str, doc_id_2_fullText: str, prompt: str) -> str:
   
   comparison_summary = compare_texts(doc_id_1_fullText, doc_id_2_fullText, prompt)
   print("Comparison completed. Saving results...")

   comparison_id = f"comparison_{datetime.utcnow().isoformat()}"
   comparison_id_added = save_comparison_result(comparison_id, doc_id_1, doc_id_2, comparison_summary)
   return {"comparison_id": comparison_id, "comparison_summary": comparison_summary, "added_id": comparison_id_added}   

