import azure.functions as func
import json
import os
from azure.cosmos import CosmosClient
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from datetime import datetime

def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        # Set CORS headers
        headers = {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type"
        }
        
        # Handle preflight requests
        if req.method == "OPTIONS":
            return func.HttpResponse(
                "",
                status_code=200,
                headers=headers
            )
        
        # Get parameters
        email = req.params.get("email")
        ticket_id = req.params.get("id")
        
        # Access Key Vault
        vault_url = "https://securevaultquickaid.vault.azure.net/"
        credential = DefaultAzureCredential()
        secret_client = SecretClient(vault_url=vault_url, credential=credential)

        # Get secrets
        endpoint = secret_client.get_secret("cosmos-endpoint").value
        key = secret_client.get_secret("cosmos-key").value

        # Connect to Cosmos DB
        client = CosmosClient(endpoint, key)
        db = client.get_database_client("QuickAidDB")
        container = db.get_container_client("Tickets")

        # Build query based on parameters
        if ticket_id:
            query = f"SELECT * FROM Tickets t WHERE t.id = '{ticket_id}'"
        elif email:
            query = f"SELECT * FROM Tickets t WHERE t.email = '{email}' ORDER BY t.timestamp DESC"
        else:
            return func.HttpResponse(
                json.dumps({"error": "Please provide either email or ticket ID parameter"}),
                status_code=400,
                headers=headers,
                mimetype="application/json"
            )

        # Execute query
        tickets = list(container.query_items(
            query=query, 
            enable_cross_partition_query=True
        ))

        # Enhance ticket data with computed fields
        for ticket in tickets:
            # Ensure status field exists
            if 'status' not in ticket:
                ticket['status'] = 'Open'
            
            # Add created_at if using timestamp
            if 'timestamp' in ticket and 'created_at' not in ticket:
                ticket['created_at'] = ticket['timestamp']
            
            # Add relative time
            if 'timestamp' in ticket:
                try:
                    ticket_time = datetime.fromisoformat(ticket['timestamp'].replace('Z', '+00:00'))
                    now = datetime.now().astimezone()
                    diff = now - ticket_time
                    
                    if diff.days > 0:
                        ticket['relative_time'] = f"{diff.days} days ago"
                    elif diff.seconds > 3600:
                        hours = diff.seconds // 3600
                        ticket['relative_time'] = f"{hours} hours ago"
                    elif diff.seconds > 60:
                        minutes = diff.seconds // 60
                        ticket['relative_time'] = f"{minutes} minutes ago"
                    else:
                        ticket['relative_time'] = "Just now"
                except:
                    ticket['relative_time'] = "Unknown"

        return func.HttpResponse(
            json.dumps(tickets),
            status_code=200,
            headers=headers,
            mimetype="application/json"
        )
        
    except Exception as e:
        error_response = {
            "error": "Failed to retrieve tickets",
            "details": str(e)
        }
        return func.HttpResponse(
            json.dumps(error_response),
            status_code=500,
            headers={
                "Access-Control-Allow-Origin": "*",
                "Content-Type": "application/json"
            },
            mimetype="application/json"
        )
