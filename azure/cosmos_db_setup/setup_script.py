from azure.cosmos import CosmosClient

endpoint = "<your_cosmos_db_endpoint>"
key = "<your_cosmos_db_key>"
database_name = "BenefitsDB"
container_name = "BenefitsContainer"

def create_cosmos_db():
    client = CosmosClient(endpoint, key)
    database = client.create_database_if_not_exists(id=database_name)
    database.create_container_if_not_exists(id=container_name, partition_key="/id")
    print(f"Database '{database_name}' and container '{container_name}' created successfully.")

if __name__ == "__main__":
    create_cosmos_db()