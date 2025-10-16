
# quickaid-frontend
This repository created is to host the frontend of the QuickAid Helpdesk system. It is shared for team collaboration purposes so that other group members can view or edit and contribute to the frontend code. 

# QuickAid – Smart Campus Helpdesk

Beginner-friendly Azure-based helpdesk app using:
- Static HTML frontend
- Python Azure Functions backend
- Cosmos DB for data storage

## Deployment

### 1. Frontend
Deploy `frontend/index.html` to Azure App Service.

### 2. Backend
Deploy `api/` using VS Code Azure Functions extension.

### 3. Cosmos DB
Create:
- Database: `QuickAidDB`
- Container: `Tickets` with partition key `/id`
Add `COSMOS_ENDPOINT` and `COSMOS_KEY` to Azure Function App settings.

<img width="3024" height="1642" alt="Screenshot 2025-10-17 at 1 02 23 AM" src="https://github.com/user-attachments/assets/bc369edb-2a93-4662-9aa9-be9dd645dee5" />
<img width="3024" height="1642" alt="Screenshot 2025-10-17 at 1 03 25 AM" src="https://github.com/user-attachments/assets/2f64dbd7-e35d-4ae2-82fc-7d33b085c711" />
<img width="3020" height="1636" alt="Screenshot 2025-10-17 at 1 03 52 AM" src="https://github.com/user-attachments/assets/98c9ab70-405e-49a0-b080-843204951dbb" />
<img width="1920" height="1260" alt="Screenshot 2025-10-17 at 1 02 49 AM" src="https://github.com/user-attachments/assets/ff8a8cc9-4903-4f2d-82b9-24ae18a95f60" />


