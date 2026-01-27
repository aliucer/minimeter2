# MiniMeter - Architecture Report

## Project Summary
AI-powered energy bill processing pipeline demonstrating LLM integration, async job processing, and multi-cloud service orchestration.

**Total Codebase:** ~1,034 lines of Python

---

## System Architecture

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
                                                         │
                                                 ┌───────▼─────────┐
                                                 │      GCS        │
                                                 │  (Artifacts)    │
                                                 └─────────────────┘
```

---

## Directory Structure

```
minimeter2/
├── api/                    # FastAPI REST API (223 lines)
│   ├── main.py             # Endpoints: /health, /customers, /agent/*
│   ├── pubsub.py           # Pub/Sub publisher
│   └── secrets.py          # Secret Manager access
│
├── worker/                 # Async job processor (529 lines)
│   ├── main.py             # Pub/Sub consumer, job lifecycle
│   ├── llm.py              # Vertex AI Gemini extraction
│   ├── storage.py          # GCS upload/download
│   ├── bigquery.py         # BigQuery insert
│   └── connectors/         # Provider connectors (tool selection)
│       ├── base.py         # BaseConnector interface
│       ├── registry.py     # Provider → Connector mapping
│       ├── mock_utility_a.py
│       └── mock_utility_b.py
│
├── shared/                 # Common modules (176 lines)
│   ├── config.py           # All environment variables
│   ├── database.py         # SQLAlchemy engine + context manager
│   ├── orm_models.py       # SQLAlchemy ORM Models (Customer, Job, Bill)
│   └── schemas.py          # Pydantic schemas (validations)
│
├── eval/                   # LLM accuracy testing
│   ├── run.py              # Eval script
│   ├── expected.json       # Ground truth
│   └── bills/              # Test bill files
│
└── docs/
    └── ARCHITECTURE.md
```

---

## Data Flow

### Full Pipeline (agent/run)

```
1. API: POST /agent/run {utility_account_id: 1}
   └── Create IngestionJob (status: PENDING)
   └── Publish to Pub/Sub (job_type: FULL_PIPELINE)

2. Worker: Receives message
   └── Update job status: RUNNING
   └── Get provider from utility_account
   └── Select connector via registry

3. Ingest Phase:
   └── Connector.fetch_bill_artifact() → raw bill text
   └── Upload to GCS: gs://minimeter-raw-data/raw/bills/{job_id}.txt
   └── Save artifact metadata to Cloud SQL

4. Parse Phase:
   └── Download bill from GCS
   └── LLM extraction (Gemini) with provider context
   └── Pydantic validation (BillNormalized)
   └── Save to Cloud SQL (normalized_bills_sql)
   └── Save to BigQuery (normalized_bills)

5. Complete:
   └── Update job status: SUCCEEDED
   └── Ack Pub/Sub message
```

---

## Key Patterns

### 1. Job Lifecycle
```
PENDING → RUNNING → SUCCEEDED
                  → FAILED (with error_message)
```
- **Idempotency:** Already SUCCEEDED jobs are skipped
- **Retry limit:** Max 3 attempts before FAILED
- **Observability:** duration_ms, attempt count logged

### 2. Tool Selection (LLM + Tools)
```python
CONNECTOR_REGISTRY = {
    "MOCK_A": MockUtilityAConnector,
    "MOCK_B": MockUtilityBConnector,
}
connector = get_connector(provider)  # Dynamic selection
```

### 3. Schema Validation
```python
# LLM output → Pydantic validation
extracted = extract_bill_data(bill_text, provider=provider)
validated = BillNormalized(**extracted)  # Raises on invalid
```

### 4. Context Manager for DB
```python
with get_db() as db:
    db.execute(...)  # Auto-commit on success, rollback on error
```

---

## GCP Services

| Service | Purpose | Resource |
|---------|---------|----------|
| Cloud Run | API hosting | minimeter-api |
| Cloud SQL | Relational data | truemeter_demo (Postgres) |
| Pub/Sub | Job queue | ingestion-jobs topic/sub |
| BigQuery | Analytics | truemeter_demo.normalized_bills |
| GCS | Artifacts | minimeter-raw-data bucket |
| Vertex AI | LLM | gemini-2.0-flash-001 |
| Secret Manager | Credentials | utility-demo-credentials |

---

## Database Tables

### Cloud SQL (Postgres)

```sql
customers (id, name, created_at)
utility_accounts (id, customer_id, provider, created_at)
ingestion_jobs (id, utility_account_id, job_type, status, error_message, attempt_count, updated_at)
artifacts (id, job_id, utility_account_id, gcs_path, artifact_type, created_at)
normalized_bills_sql (id, customer_id, utility_account_id, billing_period_start, billing_period_end, total_amount, json_payload, created_at)
```

### BigQuery

```sql
truemeter_demo.normalized_bills (customer_id, utility_account_id, bill_period_start, bill_period_end, total_amount, json_payload, created_at)
```

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | /health | Health check |
| POST | /customers | Create customer |
| GET | /customers/{id}/dashboard | Customer dashboard |
| POST | /utility-accounts | Create utility account |
| POST | /ingest/run | Low-level job trigger |
| POST | /agent/run | Start full pipeline |
| GET | /agent/result/{job_id} | Get job result |

---

## Running Locally

```bash
# Terminal 1: API
uvicorn api.main:app --reload

# Terminal 2: Worker
python -m worker.main

# Test
curl -X POST "http://localhost:8000/agent/run?utility_account_id=1"
curl http://localhost:8000/agent/result/{job_id}

# Eval
python -m eval.run
```

## Running on Cloud

The system is deployed on Google Cloud Run.

**Base URL:** `https://minimeter-api-787646377501.us-central1.run.app`

```bash
# Trigger Agent
curl -X POST "https://minimeter-api-787646377501.us-central1.run.app/agent/run?utility_account_id=1"
```

---

## File Line Counts

| Module | Lines |
|--------|-------|
| api/ | 184 |
| worker/ | 538 |
| shared/ | 234 |
| eval/ | ~80 |
| **Total** | **~1,034** |
