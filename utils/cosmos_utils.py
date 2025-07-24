from azure.cosmos import CosmosClient,partition_key
COSMOS_ENDPOINT = "-"
COSMOS_KEY = "-"
DATABASE_NAME = "tangoai-db"
CONTAINER_NAME = "documents"

client = CosmosClient(COSMOS_ENDPOINT, credential=COSMOS_KEY)

def save_file_metadata(file_name: str, blob_url:str, blob_url_sas:str, additional_data: None = None):
    """
    Save file metadata to Cosmos DB.
    
    :param file_name: The name of the file.
    :param blob_url: The URL of the uploaded blob.
    :param additional_data: Any additional data to store with the metadata.
    :return: The metadata object saved in Cosmos DB.
    """
    database = client.get_database_client(DATABASE_NAME)
    container = database.get_container_client(CONTAINER_NAME)
    # Create a metadata object
    metadata ={
        "id": file_name,
        "fileName": file_name,
        "blobUrl": blob_url,
        "blobUrlSas": blob_url_sas,
        "uploadedAt": __import__("datetime").datetime.utcnow().isoformat(),
        "additionalData": additional_data
    }
    container.upsert_item(metadata)
    return metadata

