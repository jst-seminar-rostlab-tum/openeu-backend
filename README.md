# openeu-backend

## 🚀 Running the Backend

### 1. 📦 Install dependencies
```bash
pip install -r requirements.txt
```

### 2. 🏃‍♂️ Start the FastAPI app
```bash
uvicorn main:app --reload
```

> By default, the app runs on [http://127.0.0.1:8000](http://127.0.0.1:8000)

---

## 📘 Swagger UI & OpenAPI Docs

You can test and explore the API via:

- 🧪 Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
- 📕 ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)
- 🧾 OpenAPI JSON: [http://localhost:8000/openapi.json](http://localhost:8000/openapi.json)

---
## 🧪 Mock API: `/meetings` Endpoint

This setup is currently mocked. Filtering logic and Supabase integration will be added in upcoming commits.
The FastAPI backend currently includes a mock endpoint for testing purposes.

### 📍 Endpoint
```
GET /meetings
```

### 🔎 Query Parameters
- `frequency`: `daily` | `weekly` | `monthly` (optional)
- `country`: string (optional)

### 🧾 Sample Response
```json
[
  {
    "date": "2025-05-11",
    "name": "EU Tech Summit",
    "tags": ["tech", "eu"]
  }
]
```

---
