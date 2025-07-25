from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# get environment CORS configuration
from fastapi.middleware.cors import CORSMiddleware
from config import CORS_ORIGIN_PROD, ENVIRONMENT

if ENVIRONMENT == "PRODUCTION":
    cors_origins = [CORS_ORIGIN_PROD]
else:
    cors_origins = ["http://localhost:3000", "http://127.0.0.1:8000"]

# Import FastAPI and other necessary modules
from fastapi import FastAPI, UploadFile, File, Form
app = FastAPI(
    title="Document Comparison API",
    description="API for uploading and comparing documents",
    version="1.0.0"
)
#enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)


from app.api.routes import upload,formrecognizer,comparedocuments,generatePDF
from app.api.routes.formrecognizer import RecognizeRequest
from app.services.azure_cosmos import getdocumentidbybloburl, updatedocument_withfulltext
from app.api.routes.comparedocuments import comparetwodocs       

# Include routes
app.include_router(upload.router, prefix="/api/upload", tags=["upload"])
app.include_router(formrecognizer.router, prefix="/api/formrecognizer", tags=["formrecognizer"])
app.include_router(comparedocuments.router, prefix="/api/comparedocs", tags=["comparedocs"])
app.include_router(generatePDF.router, prefix="/api/generatePDF", tags=["generatePDF"])

@app.get("/")
def read_root():
    return {"message": "Welcome to the Document Comparison API. Use the /docs endpoint to explore the API."}

@app.post("/compare")
async def compare(file1: UploadFile = File(...), file2: UploadFile = File(...), prompt: str = Form(...)):
    """
    Endpoint to compare two documents.
    Upload two files and the API will return a comparison summary.
    """
    # Upload files to Azure Blob Storage
    uploadedResponse = await upload.uploadforcompare(file1, file2)
    blob_url1 = uploadedResponse["blob_url1"]
    blob_url_sas1 = uploadedResponse["blob_url_sas1"]

    blob_url2 = uploadedResponse["blob_url2"]
    blob_url_sas2 = uploadedResponse["blob_url_sas2"]    

    get_document_id1 = getdocumentidbybloburl(blob_url1)
    get_document_id2 = getdocumentidbybloburl(blob_url2)

    # form recognizer extraction
    formregonizerResponse1 = await formrecognizer.extractsections(RecognizeRequest(blob_url=blob_url_sas1))
    formregonizerResponse2 = await formrecognizer.extractsections(RecognizeRequest(blob_url=blob_url_sas2))
    file1_readaabletxt = formregonizerResponse1["readable_text"]
    file2_readaabletxt = formregonizerResponse2["readable_text"]

    # Save the extracted text to Cosmos DB
    updatedocument_withfulltext(get_document_id1,"santhosh123",file1_readaabletxt)
    updatedocument_withfulltext(get_document_id2,"santhosh123", file2_readaabletxt)

    # Compare the two documents
    comparetwodocumentssummary = comparedocuments.comparetwodocs(
        get_document_id1, 
        get_document_id2, 
        file1_readaabletxt, 
        file2_readaabletxt, 
        prompt
    )
    #comparisonsummaryresponse = comparetwodocuments(get_document_id1, get_document_id2,file1_readaabletxt, file2_readaabletxt, prompt)
    comparison_summary = comparetwodocumentssummary["comparison_summary"]

    # Generate PDF report and upload to Azure Blob Storage , Save the comparison result in Cosmos DB
    generatePDFresponse = generatePDF.generate_upload_comparison_pdf(get_document_id1, get_document_id2, comparison_summary)
    pdfurl = generatePDFresponse["pdfurl"]
    comparison_id = generatePDFresponse["comparison_id"]
    pdfurl_sas = generatePDFresponse["pdfurl_sas"] 

    return {"pdfurl": pdfurl, "comparison_id": comparison_id , "pdf_url_sas":pdfurl_sas ,"message": "Please use the /api/comparedocuments endpoint."}