import logging
import azure.functions as func
import json
import os
import uuid
import datetime
from azure.cosmos import CosmosClient
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient 
from azure.storage.blob import BlobServiceClient
import traceback
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

# def main(req: func.HttpRequest, context: func.Context) -> func.HttpResponse:
def main(req: func.HttpRequest) -> func.HttpResponse:
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

        message = Mail (
            from_email='kojita7073@baxima.com',
            to_emails=email,
            subject='Your ticket has been received',
           html_content=f"""
                <p>Hello,</p>
                <p>Thank you for contacting QuickAid. Your ticket has been received with the following details:</p>
                <ul>
                    <li><strong>Ticket ID:</strong> {ticket['id']}</li>
                    <li><strong>Title:</strong> {ticket['title']}</li>
                    <li><strong>Category:</strong> {ticket['category']}</li>
                    <li><strong>Description:</strong> {ticket['description']}</li>
                </ul>
                <p>We will get back to you shortly.</p>
                <p>Regards,<br>QuickAid Support Team</p>
            """

            )
        
        try:
            sg = SendGridAPIClient(sendgrid_key)
            sg.send(message)
            logging.info("✅ Email successfully sent.")
        except Exception as email_error:
            logging.error(f"❌ Failed to send email: {str(email_error)}")
                
                
        return func.HttpResponse(json.dumps({
                "message": "Ticket submitted",
                "id": ticket["id"]
            }), status_code=200, mimetype="application/json")

    except Exception as e:
         logging.error("❌ An exception occurred during function execution:")
         logging.error(f"Error occurred: {str(e)}") 
    logging.error(traceback.format_exc())  # Full stack trace
    return func.HttpResponse(f"Internal Server Error: {str(e)}", status_code=500)
