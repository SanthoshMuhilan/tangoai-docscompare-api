from azure.storage.blob import BlobServiceClient

connection_string = "<your_connection_string>"
container_name = "benefits-container"

def create_blob_container():
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    container_client = blob_service_client.create_container(container_name)
    print(f"Container '{container_name}' created successfully.")

if __name__ == "__main__":
    create_blob_container()