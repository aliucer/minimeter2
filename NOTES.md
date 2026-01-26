# MiniMeter Project Notes

## GCP Project
- **Project ID**: `psychic-destiny-485404-q6`
- **Service Account**: `app-sa@psychic-destiny-485404-q6.iam.gserviceaccount.com`
- **Key File**: `psychic-destiny-485404-q6-6f7e6c295fc6.json`

## Cloud SQL (Postgres)
- **Instance**: `minimeter-db`
- **Region**: `us-central1`
- **Public IP**: `34.28.82.253`
- **Database**: `truemeter_demo`
- **User**: `postgres`
- **Password**: `demo123`
- **Connection String**: `postgresql://postgres:demo123@34.28.82.253:5432/truemeter_demo`

## Pub/Sub
- **Topic**: `ingestion-jobs`
- **Full Path**: `projects/psychic-destiny-485404-q6/topics/ingestion-jobs`

## BigQuery
- **Dataset**: `truemeter_demo`
- **Tables**:
  - `normalized_bills` (customer_id, utility_account_id, bill_period_start, bill_period_end, total_amount, json_payload, created_at)
  - `interval_usage` (customer_id, utility_account_id, ts, kwh, created_at) — partitioned by ts

## Secret Manager
- **Secret**: `utility-demo-credentials`
- **Content**: dummy JSON `{"username": "demo_user", "password": "demo_pass"}`

## Environment Variables
| Variable | Default |
|----------|---------|
| GCP_PROJECT | psychic-destiny-485404-q6 |
| DB_URL | postgresql://postgres:demo123@34.28.82.253:5432/truemeter_demo |
| PUBSUB_TOPIC | ingestion-jobs |
| BQ_DATASET | truemeter_demo |
| SECRET_NAME | utility-demo-credentials |

## Local Development

### Setup
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Run API
```bash
source venv/bin/activate
uvicorn api.main:app --reload
```

### Endpoints
| Method | Path | Description |
|--------|------|-------------|
| GET | /health | Health check |
| POST | /customers | Create customer |
| POST | /utility-accounts | Create utility account |
| POST | /ingest/run | Create job + publish to Pub/Sub |
| GET | /customers/{id}/dashboard | Customer + accounts from Cloud SQL |
| GET | /secrets/check | Verify Secret Manager access |

## DB Tables (Cloud SQL)
- `customers(id, name, created_at)`
- `utility_accounts(id, customer_id, provider, created_at)`
- `ingestion_jobs(id, utility_account_id, job_type, status, created_at)`

## Project Structure
```
minimeter2/
├── api/           # FastAPI app
│   ├── config.py  # Centralized config
│   ├── database.py
│   ├── models.py
│   ├── pubsub.py
│   ├── secrets.py
│   └── main.py
├── worker/        # Background worker (placeholder)
├── shared/        # Pydantic models
└── venv/          # Virtual environment
```

## Progress
- [x] Day 1: Repo + local running skeleton
- [x] Day 3: Cloud SQL Postgres + connection + 2 endpoints
- [x] Day 4: Pub/Sub publish + /ingest/run endpoint
- [x] Day 5: BigQuery dataset + tables (normalized_bills, interval_usage)
- [x] Day 6: Secret Manager + config + /secrets/check endpoint
- [x] Day 7: Cloud Run deploy + ARCHITECTURE.md
- [x] Week 2 Day 1: Worker consumes Pub/Sub + updates job status
- [x] Week 2 Day 2: Connector interface + GCS storage + artifacts table
- [x] Week 2 Day 3: LLM extraction (Gemini) + Pydantic validation + Cloud SQL + BigQuery
- [x] Week 2 Day 4: Agent endpoints (/agent/run, /agent/result/{job_id})
- [x] Week 2 Day 5: Tool selection (2 connectors + provider routing + LLM context)
- [x] **Polish**: Job lifecycle (PENDING→RUNNING→SUCCEEDED/FAILED)
- [x] **Polish**: Idempotency + retry limit (3 attempts)
- [x] **Polish**: Observability (duration_ms, structured logs, job context)
- [x] **Polish**: Regex fallback for LLM extraction
- [x] **Polish**: FULL_PIPELINE job type (end-to-end)
- [x] **Polish**: README demo script with architecture diagram

## Cloud Run
- **Service**: `minimeter-api`
- **Region**: `us-central1`
- **URL**: https://minimeter-api-787646377501.us-central1.run.app

## Pub/Sub
- **Subscription**: `ingestion-jobs-sub`

## Run Worker Locally
```bash
source venv/bin/activate
python -m worker.main
```
