"""Pub/Sub Worker - simplified and refactored."""
import json
import re
import time
import logging
from google.cloud import pubsub_v1

from shared.config import GCP_PROJECT, PUBSUB_SUBSCRIPTION, MAX_JOB_ATTEMPTS
from shared.database import get_db
from shared.schemas import BillNormalized

from .storage import upload_to_gcs, download_from_gcs
from .connectors import get_connector
from .llm import extract_bill_data
from .bigquery import insert_normalized_bill

# ============================================================
# LOGGING SETUP
# ============================================================

class JobContext:
    """Thread-local job context for logging."""
    job_id = "N/A"

class JobIdFilter(logging.Filter):
    def filter(self, record):
        record.job_id = JobContext.job_id
        return True

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - [job_id=%(job_id)s] %(message)s"
)
logger = logging.getLogger(__name__)
logger.addFilter(JobIdFilter())


# ============================================================
# DATABASE OPERATIONS (ORM)
# ============================================================

def get_job_info(job_id: int) -> dict:
    """Get job info including attempt count and status."""
    from shared.orm_models import IngestionJob
    with get_db() as db:
        job = db.query(IngestionJob).filter(IngestionJob.id == job_id).first()
        if job:
            return {
                "status": job.status,
                "attempt_count": job.attempt_count or 0,
                "utility_account_id": job.utility_account_id
            }
        return None


def get_account_info(utility_account_id: int) -> dict:
    """Get utility account info."""
    from shared.orm_models import UtilityAccount
    with get_db() as db:
        account = db.query(UtilityAccount).filter(UtilityAccount.id == utility_account_id).first()
        if account:
            return {"provider": account.provider, "customer_id": account.customer_id}
        # Fallback for dev/test if not found (though should exist)
        return {"provider": "MOCK_A", "customer_id": 1}


def update_job(job_id: int, status: str, error: str = None, increment_attempt: bool = False):
    """Update job status using ORM."""
    from shared.orm_models import IngestionJob
    from datetime import datetime
    
    with get_db() as db:
        job = db.query(IngestionJob).filter(IngestionJob.id == job_id).first()
        if not job:
            return

        job.status = status
        job.updated_at = datetime.utcnow()
        
        if increment_attempt:
            job.attempt_count = (job.attempt_count or 0) + 1
            
        if error:
            job.error_message = error
        elif status == "RUNNING" or status == "SUCCEEDED":
            job.error_message = None
            
        # No need to call db.commit() explicitly as context manager handles it
        # but db.add(job) is good practice though query results are tracked
        db.add(job)


def save_artifact(job_id: int, utility_account_id: int, gcs_path: str, artifact_type: str):
    """Save artifact metadata."""
    from shared.orm_models import Artifact
    with get_db() as db:
        artifact = Artifact(
            job_id=job_id,
            utility_account_id=utility_account_id,
            gcs_path=gcs_path,
            artifact_type=artifact_type
        )
        db.add(artifact)
    logger.info(f"Saved artifact: {gcs_path}")


def save_normalized_bill(customer_id: int, utility_account_id: int, bill_data: dict, json_payload: str):
    """Save normalized bill to Cloud SQL using ORM."""
    from shared.orm_models import NormalizedBillSQL
    with get_db() as db:
        bill = NormalizedBillSQL(
            customer_id=customer_id,
            utility_account_id=utility_account_id,
            billing_period_start=bill_data["billing_period_start"],
            billing_period_end=bill_data["billing_period_end"],
            total_amount=bill_data["total_amount"],
            json_payload=json_payload
        )
        db.add(bill)
    logger.info("Saved normalized bill to Cloud SQL")


# ============================================================
# FALLBACK EXTRACTION
# ============================================================

def extract_total_fallback(bill_text: str) -> float:
    """Regex fallback for total amount extraction."""
    patterns = [
        r"TOTAL\s*DUE[:\s]*\$?([\d,]+\.?\d*)",
        r"AMOUNT\s*DUE[:\s]*\$?([\d,]+\.?\d*)",
        r"Total[:\s]*\$?([\d,]+\.?\d*)",
        r"\$\s*([\d,]+\.\d{2})\s*$",
    ]
    for pattern in patterns:
        match = re.search(pattern, bill_text, re.IGNORECASE | re.MULTILINE)
        if match:
            try:
                return float(match.group(1).replace(",", ""))
            except ValueError:
                continue
    return None


# ============================================================
# JOB PROCESSORS
# ============================================================

def process_ingest(job_id: int, utility_account_id: int, provider: str) -> str:
    """Ingest bill from provider and upload to GCS."""
    connector = get_connector(provider)
    logger.info(f"Using connector for provider: {provider}")
    
    content, _ = connector.fetch_bill_artifact(utility_account_id)
    gcs_path = f"raw/bills/{job_id}.txt"
    full_path = upload_to_gcs(content, gcs_path)
    
    save_artifact(job_id, utility_account_id, full_path, "raw_bill")
    logger.info(f"Uploaded to {full_path}")
    return full_path


def process_parse(job_id: int, customer_id: int, utility_account_id: int, gcs_path: str, provider: str):
    """Parse bill with LLM and save results."""
    bill_bytes = download_from_gcs(gcs_path)
    bill_text = bill_bytes.decode("utf-8")
    logger.info(f"Downloaded bill ({len(bill_text)} chars)")
    
    # Try LLM extraction with Pydantic validation
    try:
        extracted = extract_bill_data(bill_text, provider=provider)
        validated = BillNormalized(**extracted)
        logger.info(f"Extracted: total=${validated.total_amount}, items={len(validated.line_items)}")
        
    except Exception as llm_error:
        logger.warning(f"LLM extraction failed: {llm_error}, trying fallback...")
        
        fallback_amount = extract_total_fallback(bill_text)
        if fallback_amount:
            logger.info(f"Fallback extracted total_amount: {fallback_amount}")
            # Could create partial result here, but for now we fail to trigger retry
        raise
    
    json_payload = validated.model_dump_json()
    
    # Save to SQL and BigQuery
    save_normalized_bill(customer_id, utility_account_id, extracted, json_payload)
    insert_normalized_bill(
        customer_id=customer_id,
        utility_account_id=utility_account_id,
        billing_period_start=str(validated.billing_period_start),
        billing_period_end=str(validated.billing_period_end),
        total_amount=validated.total_amount,
        json_payload=json_payload,
    )
    logger.info("Saved to BigQuery")


def process_full_pipeline(job_id: int, utility_account_id: int, customer_id: int, provider: str):
    """Full pipeline: ingest → parse."""
    gcs_path = process_ingest(job_id, utility_account_id, provider)
    process_parse(job_id, customer_id, utility_account_id, gcs_path, provider)


# ============================================================
# MESSAGE HANDLER
# ============================================================

def handle_message(message):
    """Process a Pub/Sub message."""
    start = time.time()
    job_id = None
    
    try:
        data = json.loads(message.data.decode("utf-8"))
        job_id = data.get("job_id")
        job_type = data.get("job_type")
        utility_account_id = data.get("utility_account_id")
        
        JobContext.job_id = job_id
        logger.info(f"Received: type={job_type}")
        
        # Get job info
        job_info = get_job_info(job_id)
        if not job_info:
            logger.error("Job not found in database")
            message.ack()
            return
        
        # Idempotency check
        if job_info["status"] == "SUCCEEDED":
            logger.info("Already succeeded, skipping")
            message.ack()
            return
        
        # Retry limit
        if job_info["attempt_count"] >= MAX_JOB_ATTEMPTS:
            logger.error(f"Exceeded {MAX_JOB_ATTEMPTS} attempts")
            update_job(job_id, "FAILED", "Exceeded retry limit")
            message.ack()
            return
        
        # Get account info
        account_info = get_account_info(utility_account_id)
        customer_id = data.get("customer_id") or account_info["customer_id"]
        provider = account_info["provider"]
        
        # Start processing
        update_job(job_id, "RUNNING", increment_attempt=True)
        logger.info(f"RUNNING (attempt {job_info['attempt_count'] + 1})")
        
        # Route by job type
        if job_type == "INGEST_BILL":
            process_ingest(job_id, utility_account_id, provider)
        elif job_type == "PARSE_BILL":
            gcs_path = data.get("artifact_path")
            process_parse(job_id, customer_id, utility_account_id, gcs_path, provider)
        elif job_type == "FULL_PIPELINE":
            process_full_pipeline(job_id, utility_account_id, customer_id, provider)
        
        # Success
        update_job(job_id, "SUCCEEDED")
        duration = int((time.time() - start) * 1000)
        logger.info(f"SUCCEEDED ({duration}ms)")
        message.ack()
        
    except Exception as e:
        duration = int((time.time() - start) * 1000)
        error = str(e)[:500]
        logger.error(f"FAILED: {error} ({duration}ms)")
        
        if job_id:
            update_job(job_id, "FAILED", error)
        message.nack()


# ============================================================
# MAIN
# ============================================================

def main():
    """Start the worker."""
    logger.info(f"Starting worker (subscription: {PUBSUB_SUBSCRIPTION})")
    
    subscriber = pubsub_v1.SubscriberClient()
    path = subscriber.subscription_path(GCP_PROJECT, PUBSUB_SUBSCRIPTION)
    
    future = subscriber.subscribe(path, callback=handle_message)
    logger.info("Listening for messages...")
    
    try:
        future.result()
    except KeyboardInterrupt:
        future.cancel()
        logger.info("Worker stopped")


if __name__ == "__main__":
    main()
