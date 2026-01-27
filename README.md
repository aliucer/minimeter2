# MiniMeter - AI Energy Bill Processing Demo

A demonstration of an AI-powered energy bill processing pipeline built with Python, FastAPI, and Google Cloud.

## 🚀 Live Demo

**Production API:** [https://minimeter-api-787646377501.us-central1.run.app/docs](https://minimeter-api-787646377501.us-central1.run.app/docs)

The application is deployed on Google Cloud Run with auto-scaling infrastructure. Visit the Swagger UI to explore the API endpoints interactively.

## Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   Cloud Run     │────▶│    Cloud SQL     │◀────│     Worker      │
│   (FastAPI)     │     │   (Postgres)     │     │   (Pub/Sub)     │
└────────┬────────┘     └──────────────────┘     └────────┬────────┘
         │                                                 │
         ▼                                                 ▼
    ┌─────────┐         ┌──────────────────┐     ┌─────────────────┐
    │ Pub/Sub │────────▶│  Vertex AI LLM   │     │    BigQuery     │
    └─────────┘         │    (Gemini)      │     │   (Analytics)   │
                        └──────────────────┘     └─────────────────┘
```

## Setup

### 1. Environment
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration
Copy the example environment file and update it with your credentials:
```bash
cp .env.example .env
# Edit .env with your GCP project details and database URL
```

## ☁️ Cloud Demo (No Setup Required)

You can interact with the live deployed API directly.

### 1. Create a Job
Trigger the AI agent for an existing utility account (ID: 1):

```bash
curl -X POST "https://minimeter-api-787646377501.us-central1.run.app/agent/run" \
  -H "Content-Type: application/json" \
  -d '{"utility_account_id": 1}'
```

**Response:**
```json
{"job_id": 123, "message": "Agent job started..."}
```

### 2. Check Results
Replace `123` with your `job_id`:

```bash
curl "https://minimeter-api-787646377501.us-central1.run.app/agent/result/123"
```

---

## 💻 Local Demo (5 commands)

### 1. Start the services
```bash
# Terminal 1: Start API
source venv/bin/activate
uvicorn api.main:app --reload

# Terminal 2: Start Worker
source venv/bin/activate
python -m worker.main
```

### 2. Run the AI Agent
```bash
# Create a customer and utility account (if not exists)
curl -X POST http://localhost:8000/customers \
  -H "Content-Type: application/json" \
  -d '{"name": "Demo Company"}'

curl -X POST http://localhost:8000/utility-accounts \
  -H "Content-Type: application/json" \
  -d '{"customer_id": 1, "provider": "MOCK_A"}'

# Start the AI agent pipeline
curl -X POST http://localhost:8000/agent/run \
  -H "Content-Type: application/json" \
  -d '{"utility_account_id": 1}'
```

**Expected Output:**
```json
{"job_id": 1, "message": "Agent job started. Poll /agent/result/{job_id} for results."}
```

### 3. Check the result
```bash
# Wait 2-3 seconds for processing, then:
curl http://localhost:8000/agent/result/1
```

**Expected Output:**
```json
{
  "job_id": 1,
  "status": "SUCCEEDED",
  "result": {
    "billing_period_start": "2025-12-01",
    "billing_period_end": "2025-12-31",
    "total_amount": 106.40,
    "json_payload": "{\"line_items\": [{\"name\": \"Basic Service Charge\", \"amount\": 12.0}, ...]}"
  }
}
```

## What Happens Under the Hood

1. **API** creates a job record and publishes to Pub/Sub
2. **Worker** picks up the message from the queue
3. **Connector** fetches the bill from the utility provider (mock)
4. **GCS** stores the raw bill artifact
5. **LLM (Gemini)** extracts structured data from the bill text
6. **Pydantic** validates the extracted JSON
7. **Cloud SQL + BigQuery** store the normalized result

## Key Features

- **LLM + Tools**: Provider-based connector selection (tool routing)
- **Schema Validation**: Pydantic models for strict output format
- **Job Lifecycle**: PENDING → RUNNING → SUCCEEDED/FAILED with retry
- **Idempotency**: Same job won't be processed twice
- **Observability**: Structured logs with job_id, duration_ms, attempt count

## GCP Services Used

| Service | Purpose |
|---------|---------|
| Cloud Run | API hosting |
| Cloud SQL | Job state, customers, normalized bills |
| Pub/Sub | Async job queue |
| BigQuery | Analytics data warehouse |
| GCS | Raw bill artifact storage |
| Vertex AI | LLM extraction (Gemini) |
| Secret Manager | Credentials storage |

## Project Structure

```
minimeter2/
├── api/              # API Service (FastAPI)
├── worker/           # Processing Service (Asynchronous Worker)
├── shared/           # Shared Schemas & Database Models
├── docs/             # Technical Documentation
├── eval/             # Evaluation & Testing Suite
├── test_pipeline.sh  # Local E2E Pipeline Test
└── test_cloud.sh    # Cloud Deployment Verification
```

## Testing

### Automated E2E Tests
Run the full pipeline locally:
```bash
./test_pipeline.sh
```

Test against the live Cloud Run deployment:
```bash
./test_cloud.sh
```

Both scripts will create a customer, utility account, trigger the AI agent, and verify the extracted bill data.