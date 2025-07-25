from config import AZURE_STORAGE_CONNECTION_STRING, AZURE_BLOB_CONTAINER_NAME_UPLOADS
from azure.storage.blob import BlobServiceClient, generate_blob_sas, BlobSasPermissions
from datetime import datetime, timedelta

#Get your Azure Storage connection string from the Azure portal
#AzureStorageConnectionString = AZURE_STORAGE_CONNECTION_STRING
#blob_container_name = AZURE_BLOB_CONTAINER_NAME_UPLOADS

#Crete a BlobServiceClient object
blob_service_client = BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)
container_client = blob_service_client.get_container_client(AZURE_BLOB_CONTAINER_NAME_UPLOADS)

async def upload_to_blob(file):
    """
    Upload a file to Azure Blob Storage and return the blob URL.
    
    :param file: The file to upload.
    :return: The URL of the uploaded blob.
    """
    blob_name = file.filename
    try:
        container_client.upload_blob(name=blob_name, data=file.file, overwrite=True)
        blob_url = f"https://{blob_service_client.account_name}.blob.core.windows.net/{AZURE_BLOB_CONTAINER_NAME_UPLOADS}/{blob_name}"
        return blob_url
    except Exception as e:
        print(f"Failed to upload file: {e}")
        return None

async def generate_sas_url(blob_name: str, expiry_minutes: int = 30) -> str:   
   sas_token = generate_blob_sas(
       account_name=blob_service_client.account_name,
       container_name=AZURE_BLOB_CONTAINER_NAME_UPLOADS,
       blob_name=blob_name,
       account_key=blob_service_client.credential.account_key,
       permission=BlobSasPermissions(read=True),
       expiry=datetime.utcnow() + timedelta(minutes=expiry_minutes)
   )
   blob_client = blob_service_client.get_blob_client(AZURE_BLOB_CONTAINER_NAME_UPLOADS, blob_name)
   #sas_url = f"{blob_client.url}?{sas_token}"
   sas_url = f"https://{blob_service_client.account_name}.blob.core.windows.net/{AZURE_BLOB_CONTAINER_NAME_UPLOADS}/{blob_name}?{sas_token}"
   return sas_url
