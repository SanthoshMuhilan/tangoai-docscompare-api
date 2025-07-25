from config import AZURE_STORAGE_CONNECTION_STRING, AZURE_BLOB_CONTAINER_NAME_REPORTS
from fastapi import APIRouter, UploadFile, File, Form
from fpdf import FPDF
from io import BytesIO
from datetime import datetime
from azure.storage.blob import BlobServiceClient,generate_blob_sas, BlobSasPermissions
from app.services.azure_cosmos import save_comparison_result  # your existing function
from datetime import datetime, timedelta

router = APIRouter()

# Azure Blob Storage Config
AZURE_BLOB_CONNECTION_STRING = AZURE_STORAGE_CONNECTION_STRING
BLOB_CONTAINER_NAME = AZURE_BLOB_CONTAINER_NAME_REPORTS  # Must exist

# Initialize Azure Blob client
blob_service_client = BlobServiceClient.from_connection_string(AZURE_BLOB_CONNECTION_STRING)
container_client_blob = blob_service_client.get_container_client(BLOB_CONTAINER_NAME)

@router.post("/generatePDF")
def generate_upload_comparison_pdf(doc_id_1: str, doc_id_2: str, summary: str, metadata: dict = None) -> dict:
   pdf = FPDF()
   pdf.add_page()

   # Add title
   pdf.set_font("Arial", 'B', size=16)
   pdf.cell(0, 10, f"Comparison Report: {doc_id_1} vs {doc_id_2}", ln=True, align='C')
   pdf.ln(10)

   # Add content
   pdf.set_font("Arial", size=12)
   pdf.multi_cell(0, 10, summary)

   # Output PDF to BytesIO buffer
   pdf_buffer = BytesIO()
   pdf_byte = pdf.output(dest='S').encode('latin1')  # Get PDF as bytes
   pdf_buffer.write(pdf_byte)
   pdf_buffer.seek(0)

   # === Step 2: Upload to Azure Blob Storage ===
   timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
   filename = f"comparison_{doc_id_1}_vs_{doc_id_2}_{timestamp}.pdf"
   
   blob_client = container_client_blob.get_blob_client(filename)
   blob_client.upload_blob(pdf_buffer, overwrite=True)
   blob_url = blob_client.url
   print(f" PDF uploaded to Blob Storage: {blob_url}")
   pdf_buffer.close()  # Close the buffer

   sas_token = generate_blob_sas(
       account_name=blob_service_client.account_name,
       container_name=BLOB_CONTAINER_NAME,
       blob_name=filename,
       account_key=blob_service_client.credential.account_key,
       permission=BlobSasPermissions(read=True),
       expiry=datetime.utcnow() + timedelta(minutes=30)
   )
   blob_client_sas = blob_service_client.get_blob_client(BLOB_CONTAINER_NAME, filename)
   pdf_bloburl_sas = f"https://{blob_service_client.account_name}.blob.core.windows.net/{BLOB_CONTAINER_NAME}/{filename}?{sas_token}"
   print(f"Generated SAS URL for PDF: {pdf_bloburl_sas}")

   print("Comparison completed. Saving results...")
   comparison_id = f"Comparison_{doc_id_1}_vs_{doc_id_2}_{datetime.utcnow().isoformat()}"
   comparisonidadded = save_comparison_result(comparison_id, doc_id_1, doc_id_2, summary, blob_url,pdf_bloburl_sas, metadata)
   print(f"Comparison saved with ID: {comparison_id}")
   
   return { "pdfurl": blob_url, "pdfurl_sas": pdf_bloburl_sas, "comparison_id": comparison_id }