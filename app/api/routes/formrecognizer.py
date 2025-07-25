from config import AZURE_FORM_RECOGNIZER_ENDPOINT, AZURE_FORM_RECOGNIZER_KEY
from fastapi import FastAPI,APIRouter, HTTPException
from pydantic import BaseModel
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
import json

router = APIRouter()

#Form recognizer credentials
#FORM_RECOGNIZER_ENDPOINT = AZURE_FORM_RECOGNIZER_ENDPOINT
#FORM_RECOGNIZER_KEY = AZURE_FORM_RECOGNIZER_KEY

#initialize the DocumentAnalysisClient
form_recognizer_client = DocumentAnalysisClient(
    endpoint=AZURE_FORM_RECOGNIZER_ENDPOINT,
    credential=AzureKeyCredential(AZURE_FORM_RECOGNIZER_KEY)
)

class RecognizeRequest(BaseModel):
    blob_url: str

@router.post("/extractsections")
async def extractsections(request: RecognizeRequest):
    try:
        poller = form_recognizer_client.begin_analyze_document_from_url(
            "prebuilt-document",
            request.blob_url
        )
        result = poller.result()

        sections = []

        #extract pages ,lines and tables
        for page in result.pages:
            page_data = {
                "page_number": page.page_number,
                "lines": [line.content for line in page.lines],
                "tables": []  # Initialize tables as an empty list
            }
            sections.append(page_data)
        #Extract Tables
        for table in result.tables:
            if table.bounding_regions[0].page_number == page.page_number:
                table_rows = [[] for _ in range(table.row_count)]
                for cell in table.cells:
                    table_rows[cell.row_index].append(cell.content)
                page_data["tables"].append(table_rows)
        sections.append(page_data)
        document_section = ""
        #document_section = json.dumps(result.to_dict(),indent=2)
        
        # Append the fields extracted from the document
        
        readable_text = []
        readable_text.append("--- Document Summary ---")
        for page in result.pages:
            readable_text.append(f"\n Page {page.page_number}\n")
            # Extract lines (paragraphs, headers)
            for line in page.lines:
                content = line.content.strip()
                if content:
                    readable_text.append(f" {content}")
            # Extract tables
            if result.tables:
                for idx, table in enumerate(result.tables, start=1):
                    readable_text.append("\n Table {idx}:")
                    # Build table header
                    max_row = max(cell.row_index for cell in table.cells) + 1
                    max_col = max(cell.column_index for cell in table.cells) + 1
                    # Initialize table grid
                    table_grid = [["" for _ in range(max_col)] for _ in range(max_row)]
                    for cell in table.cells:
                        table_grid[cell.row_index][cell.column_index] = cell.content.strip()
                    # Format table
                    for row in table_grid:
                        row_text = "| " + " | ".join(row) + " |"
                        readable_text.append(row_text)                    
        #readabletext = "\n".join(readable_text)

        #return {"success": "true", "sections": sections, "document_section": document_section, "readable_text": readable_text} 
        return {"success": "true", "readable_text": readable_text} 
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))   