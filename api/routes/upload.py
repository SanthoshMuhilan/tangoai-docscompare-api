from fastapi import APIRouter, UploadFile, File
from app.services.azure_blob import upload_to_blob, generate_sas_url
from app.services.azure_cosmos import save_file_metadata

router = APIRouter()

@router.post("/upload-document")
async def upload_document(file: UploadFile = File(...)):
    blob_url = await upload_to_blob(file)
    blob_url_sas = await generate_sas_url(file.filename)

    #save metadata to Cosmos DB
    metadata1 = save_file_metadata(file.filename, blob_url, blob_url_sas)

    
    return {"blob_url": blob_url, "blob_url_sas": blob_url_sas, "message": "File uploaded successfully."}

@router.post("/uploadforcompare")
async def uploadforcompare(file1: UploadFile = File(...), file2: UploadFile = File(...)):
    #upload both files to blob storage
    blob_url1 = await upload_to_blob(file1)
    blob_url2 = await upload_to_blob(file2)

    blob_url_sas1 = await generate_sas_url(file1.filename)
    blob_url_sas2 = await generate_sas_url(file2.filename)
    
    #save metadata to Cosmos DB
    metadata1 = save_file_metadata(file1.filename, blob_url1, blob_url_sas1, "purpose: comparison")
    metadata2 = save_file_metadata(file2.filename, blob_url2, blob_url_sas2, "purpose: comparison")    
    
    return { "blob_url1": blob_url1, "blob_url_sas1": blob_url_sas1, "blob_url2": blob_url2, "blob_url_sas2": blob_url_sas2,"file1": metadata1, "file2": metadata2, "message": "Files uploaded for comparison successfully." }

