import uuid
from datetime import datetime
from config import COSMOS_ENDPOINT, COSMOS_KEY, DATABASE_NAME, DOCUMENT_CONTAINER_NAME, EMBEDDING_CONTAINER_NAME, COMPARISON_CONTAINER_NAME, CHAT_CONTAINER_NAME
from azure.cosmos import CosmosClient,partition_key

client = CosmosClient(COSMOS_ENDPOINT, credential=COSMOS_KEY)
database = client.get_database_client(DATABASE_NAME)

def save_file_metadata(file_name: str, blob_url:str, blob_url_sas:str, additional_data: None = None):
    """
    Save file metadata to Cosmos DB.
    
    :param file_name: The name of the file.
    :param blob_url: The URL of the uploaded blob.
    :param additional_data: Any additional data to store with the metadata.
    :return: The metadata object saved in Cosmos DB.
    """    
    container = database.get_container_client(DOCUMENT_CONTAINER_NAME)
    
    # Create a metadata object
    metadata ={
        "id": file_name,
        "fileName": file_name,
        "blobUrl": blob_url,
        "blobUrlSas": blob_url_sas,
        "uploadedAt": __import__("datetime").datetime.utcnow().isoformat(),
        "additionalData": additional_data,
        "userId": "santhosh123"  # Example user ID, replace with actual user ID if available
    }
    container.upsert_item(metadata)
    return metadata

def getdocumentidbybloburl(blob_url: str):
    """
    Retrieve the document ID from Cosmos DB based on the blob URL.
    
    :param blob_url: The URL of the blob.
    :return: The document ID if found, otherwise None.
    """
    
    container = database.get_container_client(DOCUMENT_CONTAINER_NAME)    
    query = "SELECT c.id FROM c WHERE c.blobUrl = @blobUrl"
    parameters = [{"name": "@blobUrl", "value": blob_url}]
    
    items = list(container.query_items(query=query, parameters=parameters, enable_cross_partition_query=True))
    
    if items:
        return items[0]["id"]
    return None

def updatedocument_withfulltext(doc_id:str, user_id:str, full_text:str):
    """
    Update the document in Cosmos DB with full text.
    
    :param doc_id: The ID of the document to update.
    :param full_text: The full text to store in the document.
    """
    
    container = database.get_container_client(DOCUMENT_CONTAINER_NAME)    
    # Retrieve the existing document
    item = container.read_item(item=doc_id, partition_key=user_id)
    
    # Update the full text field
    item["fullText"] = full_text
    
    # Upsert the updated item
    container.upsert_item(item) 

def save_chunk(document_id: str, chunk_id: int, text: str, embedding: list):
   """Save chunk and embedding to Cosmos DB"""   
   embedding_container = database.get_container_client(EMBEDDING_CONTAINER_NAME)
   item = {
       "id": f"{document_id}_chunk_{chunk_id}",
       "documentId": document_id,
       "chunkId": chunk_id,
       "text": text,
       "embedding": embedding
   }
   embedding_container.upsert_item(item)  

def fetch_chunks_by_document(document_id: str):
    """Fetch all chunks for a given document ID"""    
    embedding_container = database.get_container_client(EMBEDDING_CONTAINER_NAME)    
    query = f"SELECT c.text, c.embedding FROM c WHERE c.documentId = '{document_id}'"
    chunks = []
    embeddings = []
    
    for item in embedding_container.query_items(query=query, enable_cross_partition_query=True):
        chunks.append(item['text'])
        embeddings.append(item['embedding'])
    print(f"Fetched {len(chunks)} chunks for document {document_id}")
    return chunks, embeddings

def save_comparison_result(comparison_id:str, doc_id_1: str, doc_id_2: str, summary: str, pdf_url: str = None,pdf_url_sas: str = None, metadata: dict = None):
    
    comparison_container = database.get_container_client(COMPARISON_CONTAINER_NAME)
    #comparison_id = str(uuid.uuid4())  # Generate unique ID
    item = {
        "id": comparison_id,
        "docId1": doc_id_1,
        "docId2": doc_id_2,
        "summary": summary,
        "pdfUrl": pdf_url,
        "pdfUrlSaS": pdf_url_sas,
        "createdAt": datetime.utcnow().isoformat(),
        "metadata": metadata or {}
    }
    # Insert into Cosmos DB
    comparison_container.upsert_item(item)
    print(f" Comparison result saved to Cosmos DB with ID: {comparison_id}")
    return comparison_id    

def save_chat_result(chat_data: dict) -> str:   
   chat_container = database.get_container_client(CHAT_CONTAINER_NAME)
   chat_data["id"] = str(uuid.uuid4())
   chatcontainer.upsert_item(chat_data)
   print(f" Chat saved with ID: {chat_data['id']}")
   return chat_data["id"]

def fetch_chat_history(document_id: str, limit: int = 50, sort_order: str = "asc") -> list:
    oreder = "ASC" if sort_order.lower() == "asc" else "DESC"
    query = (
        f"SELECT * FROM c "
        f"WHERE c.documentId='{document_id}' "
        f"ORDER BY c.createdAt {order} OFFSET 0 LIMIT {limit}"
    )
    chat_container = client.get_database_client(DATABASE_NAME).get_container_client(CHAT_CONTAINER_NAME)
    chats = list(chat_container.query_items(
        query=query,
        enable_cross_partition_query=True
    ))
    print(f"Fetched {len(chats)} chat(s) for Document ID: {document_id}")
    return chats
