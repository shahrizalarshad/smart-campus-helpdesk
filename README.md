
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

<img width="3024" height="1642" alt="home" src="https://github.com/user-attachments/assets/5b733693-f3f7-4581-a97b-71c29c521b62" />
<img width="3016" height="1638" alt="create" src="https://github.com/user-attachments/assets/ea9e75e7-f67f-45cd-aa48-e60f2ee02afa" />
<img width="3024" height="1642" alt="check" src="https://github.com/user-attachments/assets/ae08faf2-8962-4469-becf-3ed9b265d984" />
<img width="3020" height="1636" alt="qna" src="https://github.com/user-attachments/assets/5392ccaf-e695-44f8-8e82-886db5cc9d14" />



