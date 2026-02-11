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

Fetches UK payment statistics from the Bank of England API.

> **Full Documentation:** See [docs/payments.md](docs/payments.md) for detailed API responses, frontend integration, and scheduler info.

### Routes
#### GET /stats
Returns main dashboard statistics (consumer credit, credit cards, mortgages, bank rate) with month-over-month changes.

#### GET /payment-methods
Returns UK payment method market share breakdown (debit cards, credit cards, etc.)

#### GET /trend-alerts
Returns alerts for metrics with significant changes (>5%)

#### POST /refresh
Manually triggers a data refresh from the Bank of England API

### Scheduler
Data is automatically refreshed daily at 6:00 AM UTC via APScheduler.

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
#### legislation
Contains all docs for scraped legislation
#### market_trends
Contains all docs for scraped market_trends

---

# Frontend Integration

## Backend-Frontend Communication

### API Base URL
```
Development: http://localhost:8000/api/v1
Production: https://your-domain.com/api/v1
```

### CORS Configuration
The backend allows requests from `http://localhost:5173` (Vite default). Update `main.py` for production origins.

### Request/Response Format
- All requests and responses use **JSON**
- Use `Content-Type: application/json` headers
- Dates are returned in **ISO 8601** format

### Authentication
Currently no authentication required. Add JWT/API keys for production.

### Example Fetch Pattern (TypeScript)
```typescript
const API_BASE = 'http://localhost:8000/api/v1';

async function fetchFromAPI<T>(endpoint: string): Promise<T> {
  const response = await fetch(`${API_BASE}${endpoint}`);
  if (!response.ok) {
    throw new Error(`API Error: ${response.status}`);
  }
  return response.json();
}

// Usage
const stats = await fetchFromAPI<PaymentStatsResponse>('/payment/stats');
```

### Error Handling
API errors return:
```json
{
  "detail": "Error message here"
}
```

Handle with:
```typescript
try {
  const data = await fetchFromAPI('/payment/stats');
} catch (error) {
  // Show user-friendly error
  console.error('Failed to load data');
}
```

### Recommended Frontend Libraries
- **Data fetching:** React Query / SWR / TanStack Query
- **Charts:** Recharts / Chart.js / ApexCharts
- **State:** React Context / Zustand / Redux Toolkit

### Sample React Query Setup
```typescript
import { useQuery } from '@tanstack/react-query';

function usePaymentStats() {
  return useQuery({
    queryKey: ['paymentStats'],
    queryFn: () => fetchFromAPI<PaymentStatsResponse>('/payment/stats'),
    staleTime: 5 * 60 * 1000, // 5 minutes
    refetchInterval: 10 * 60 * 1000, // Refetch every 10 min
  });
}

// In component
function Dashboard() {
  const { data, isLoading, error } = usePaymentStats();
  
  if (isLoading) return <Skeleton />;
  if (error) return <ErrorMessage />;
  return <StatsDisplay data={data} />;
}
```

---

# Documentation
- **Payment System:** [docs/payments.md](docs/payments.md) - Full API docs, data handling, frontend recommendations