import azure.functions as func
import json
import os
import uuid
import logging
from azure.cosmos import CosmosClient
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient 
from azure.storage.blob import BlobServiceClient
import traceback

def main(req: func.HttpRequest, context: func.Context) -> func.HttpResponse:
    logging.info("submit_ticket function triggered.")

    try:
        # Parse request JSON body first
        try:
            data = req.get_json()
            logging.info(f"Request data received: {data}")
        except Exception as json_error:
            logging.error(f"Failed to parse JSON body: {json_error}")
            return func.HttpResponse("Invalid JSON format in request body.", status_code=400)

        # Get fields from request body
        email = data.get("email")
        title = data.get("title")
        category = data.get("category")
        description = data.get("description")

        if not all([email, title, category, description]):
            logging.warning("Missing one or more required fields.")
            return func.HttpResponse("Missing required fields in the request.", status_code=400)

        # Access Key Vault
        vault_url = "https://securevaultquickaid.vault.azure.net/"
        credential = DefaultAzureCredential()
        secret_client = SecretClient(vault_url=vault_url, credential=credential)

        # Get secrets
        endpoint = secret_client.get_secret("cosmos-endpoint").value
        key = secret_client.get_secret("cosmos-key").value 
        sendgrid_key = secret_client.get_secret("sendgrid-api-key").value
        storage_credentials = secret_client.get_secret("storagecredentials").value

        # Upload dummy file to blob storage
        blob_service_client = BlobServiceClient.from_connection_string(storage_credentials)
        container_name = "tickets"
        blob_name = f"ticket-{uuid.uuid4()}.txt"
        blob_content = "This is a sample uploaded ticket file."
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
        blob_client.upload_blob(blob_content, overwrite=True)

        # Create ticket object
        ticket = {
            "id": str(uuid.uuid4()),
            "title": title,
            "email": email,
            "category": category,
            "description": description,
            "status": "New"
        }

        # Store to Cosmos DB
        client = CosmosClient(endpoint, key)
        db = client.get_database_client("QuickAidDB")
        container = db.get_container_client("Tickets")
        container.create_item(body=ticket)

        return func.HttpResponse(json.dumps({
            "message": "Ticket submitted",
            "id": ticket["id"]
        }), status_code=200, mimetype="application/json")

    except Exception as e:
         logging.error("❌ An exception occurred during function execution:")
         logging.error(f"Error occurred: {str(e)}") 
    logging.error(traceback.format_exc())  # Full stack trace
    return func.HttpResponse(f"Internal Server Error: {str(e)}", status_code=500)
