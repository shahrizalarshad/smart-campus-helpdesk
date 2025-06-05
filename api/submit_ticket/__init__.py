import azure.functions as func
import json
import os
import uuid
from azure.cosmos import CosmosClient
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient 
from azure.storage.blob import BlobServiceClient, BlobClient
from werkzeug.datastructures import FileStorage 
from io import BytesIO 

def main(req: func.HttpRequest) -> func.HttpResponse:
    try:

        #Setup Keyvault access 
        vault_url = "https://securevaultquickaid.vault.azure.net/"
        credential =  DefaultAzureCredential()
        secret_client = SecretClient(vault_url=vault_url, credential=credential)

        #Get secrets
        endpoint = secret_client.get_secret("cosmos-endpoint").value
        key = secret_client.get_secret("cosmos-key").value 
        sendgrid_key = secret_client.get_secret("sendgrid-api-key").value
        storage_credentials = secret_client.get_secret("storagecredentials").value

         # Sample logic: upload a simple text file to Blob
        blob_service_client = BlobServiceClient.from_connection_string(storage_credentials)
        container_name = "Tickets"  # Must already exist
        blob_name = f"ticket-{uuid.uuid4()}.txt"
        blob_content = "This is a sample uploaded ticket file."

        blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
        blob_client.upload_blob(blob_content, overwrite=True)

        #Proceed with ticket logic 
        data = req.get_json()
        ticket = {
            "id": str(uuid.uuid4()),
            "title": data.get("title"),
            "email": data.get("email"),
            "category": data.get("category"),
            "description": data.get("description"),
            "status": "New"
        }

        # endpoint = os.environ["COSMOS_ENDPOINT"]
        # key = os.environ["COSMOS_KEY"]
        client = CosmosClient(endpoint, key)
        db = client.get_database_client("QuickAidDB")
        container = db.get_container_client("Tickets")
        container.create_item(body=ticket)

        return func.HttpResponse(json.dumps({"message": "Ticket submitted", "id": ticket["id"]}),
                                 status_code=200,
                                 mimetype="application/json")
    except Exception as e:
        return func.HttpResponse(str(e), status_code=500)
