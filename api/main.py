"""MiniMeter API."""
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text

from shared import (
    get_db_dependency, Base, engine,
    CustomerCreate, UtilityAccountCreate, IngestRunRequest,
    HealthResponse, CustomerResponse, UtilityAccountResponse, JobResponse, AgentResultResponse, BillResult,
    Customer, UtilityAccount, IngestionJob, NormalizedBillSQL
)
from .pubsub import publish_job
from .secrets import check_secret_access


# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="MiniMeter API", description="AI-powered energy bill processing", version="1.0.0")


# ============================================================
# HEALTH
# ============================================================

@app.get("/health", response_model=HealthResponse)
def health():
    return {"ok": True}


@app.get("/secrets/check", response_model=HealthResponse)
def secrets_check():
    if check_secret_access():
        return {"ok": True}
    raise HTTPException(status_code=500, detail="Cannot access secret")


# ============================================================
# CUSTOMERS
# ============================================================

@app.post("/customers", response_model=CustomerResponse)
def create_customer(data: CustomerCreate, db: Session = Depends(get_db_dependency)):
    customer = Customer(name=data.name)
    db.add(customer)
    db.commit()
    db.refresh(customer)
    return {"id": customer.id, "name": customer.name, "created_at": str(customer.created_at)}


@app.get("/customers/{customer_id}/dashboard")
def get_dashboard(customer_id: int, db: Session = Depends(get_db_dependency)):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    accounts = db.query(UtilityAccount).filter(UtilityAccount.customer_id == customer_id).all()
    return {
        "customer": {"id": customer.id, "name": customer.name},
        "utility_accounts": [{"id": a.id, "provider": a.provider} for a in accounts],
    }


# ============================================================
# UTILITY ACCOUNTS
# ============================================================

@app.post("/utility-accounts", response_model=UtilityAccountResponse)
def create_utility_account(data: UtilityAccountCreate, db: Session = Depends(get_db_dependency)):
    account = UtilityAccount(customer_id=data.customer_id, provider=data.provider)
    db.add(account)
    db.commit()
    db.refresh(account)
    return {"id": account.id, "customer_id": account.customer_id, "provider": account.provider, "created_at": str(account.created_at)}


# ============================================================
# INGEST (Low-level)
# ============================================================

@app.post("/ingest/run", response_model=JobResponse)
def run_ingest(data: IngestRunRequest, db: Session = Depends(get_db_dependency)):
    job = IngestionJob(utility_account_id=data.utility_account_id, job_type=data.job_type, status="PENDING")
    db.add(job)
    db.commit()
    db.refresh(job)
    publish_job(job.id, data.utility_account_id, data.job_type)
    return {"job_id": job.id, "status": job.status, "message": "Job created"}


# ============================================================
# AGENT (High-level)
# ============================================================

@app.post("/agent/run", response_model=JobResponse)
def agent_run(utility_account_id: int, db: Session = Depends(get_db_dependency)):
    """Start AI agent for end-to-end bill processing."""
    account = db.query(UtilityAccount).filter(UtilityAccount.id == utility_account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Utility account not found")
    
    job = IngestionJob(utility_account_id=utility_account_id, job_type="FULL_PIPELINE", status="PENDING")
    db.add(job)
    db.commit()
    db.refresh(job)
    
    publish_job(job.id, utility_account_id, "FULL_PIPELINE", customer_id=account.customer_id)
    return {"job_id": job.id, "status": job.status, "message": f"Poll /agent/result/{job.id}"}


@app.get("/agent/result/{job_id}", response_model=AgentResultResponse)
def agent_result(job_id: int, db: Session = Depends(get_db_dependency)):
    """Get agent job result."""
    job = db.query(IngestionJob).filter(IngestionJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if job.status == "FAILED":
        return {"job_id": job_id, "status": "FAILED", "error": getattr(job, "error_message", None)}
    
    if job.status != "SUCCEEDED":
        return {"job_id": job_id, "status": job.status, "message": f"Job is {job.status}"}
    
    result = db.query(NormalizedBillSQL).filter(
        NormalizedBillSQL.utility_account_id == job.utility_account_id
    ).order_by(NormalizedBillSQL.created_at.desc()).first()

    
    if not result:
        return {"job_id": job_id, "status": "SUCCEEDED", "message": "No bill data"}
    
    return {
        "job_id": job_id,
        "status": "SUCCEEDED",
        "result": {
            "billing_period_start": str(result.billing_period_start),
            "billing_period_end": str(result.billing_period_end),
            "total_amount": result.total_amount,
            "json_payload": result.json_payload,
        }
    }
