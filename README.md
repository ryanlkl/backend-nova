# backend-nova
## Project Initialisation
In your terminal, run:
```python -m venv venv```
```venv/Scripts/Activate```
```pip install -r requirements.txt```

To run the ChromaDB Server:
```chroma run --host localhost --port 8080 --path ./my_chroma_data```

To run FastAPI Backend:
```uvicorn main:app --reload --port 8000```

# Endpoints
**Base URL:** http:localhost:8000/api/v1
## Agent
**Route:** /agent
### Routes
#### POST /
Sends query to agent to process and returns response.

Request Body:
{
"query": `<string>`
}

Response Format:

## Market Trends
**Route:** /market
### Routes
#### GET /
Returns all market trend info from PostgreSQL database for data display
#### GET /{id}
Returns corresponding object to SQL row

## Legislation
**Route:** /legislation
### Routes
#### GET /
Returns all legislation info from PostgreSQL database for data display
#### GET /{id}
Returns corresponding object to SQL row

## Payment Data
**Route:** /payment
### Routes
#### GET /
Returns all legislation info from PostgreSQL database for data display
#### GET /{id}
Returns corresponding SQL row

## Content Hub
**Route:** /content
### Routes
#### GET /
Retrieves all stored content hub data from PostgreSQL database for data display
#### GET /{id}
Returns corresponding SQL row
#### GET /{id}/download
Retrieves object from bucket and returns in response to allow for download
#### POST /
Receives file and relevant metadata to store in SQL database and upload to object storage with relevant metadata

Request Body:
#### DELETE /{id}
Deletes all stored information in all storage types for the corresponding id

## Notifications
**Route:** /notification
### Routes
#### GET /
Retrieves all notifications
#### GET /{id}
Retrieves information based on corresponding notification
#### PATCH /{id}
Updates notification content
#### DELETE /{id}
Deletes all corresponding notification information
# Storage
## PostgreSQL (Supabase)
### Schema
#### Legislation

```
id UUID PK
title TEXT
description TEXT Nullable
source TEXT
file_type ENUM("pdf", "docx", "csv", "xlsx", "pptx")
created_at TEXT DEFAULT=datetime.now() (ISO Format)
updated_at TEXT DEFAULT=datetime.now() (ISO Format)
```

#### Market Data

```
id UUID PK
title TEXT UNIQUE
description TEXT Nullable
source TEXT
file_type ENUM("pdf", "docx", "csv", "xlsx", "pptx")
created_at TEXT DEFAULT=datetime.now() (ISO Format)
updated_at TEXT DEFAULT=datetime.now() (ISO Format)
```
## Object Storage (AWS S3)
### Buckets
#### nova-legislation-bucket
Contains all pdf's of legislation
#### nova-content-bucket
This will be where all the content from content hub will be uploaded and downloaded from
## Vector Database (Chroma DB)
### Collections
