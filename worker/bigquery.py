"""BigQuery helper for writing normalized bills."""
from datetime import datetime
from google.cloud import bigquery
from shared.config import GCP_PROJECT, BQ_DATASET

client = bigquery.Client(project=GCP_PROJECT)
TABLE = "normalized_bills"


def insert_normalized_bill(
    customer_id: int,
    utility_account_id: int,
    billing_period_start: str,
    billing_period_end: str,
    total_amount: float,
    json_payload: str,
):
    """Insert a normalized bill record into BigQuery."""
    table_id = f"{GCP_PROJECT}.{BQ_DATASET}.{TABLE}"
    
    rows = [{
        "customer_id": customer_id,
        "utility_account_id": utility_account_id,
        "bill_period_start": billing_period_start,
        "bill_period_end": billing_period_end,
        "total_amount": total_amount,
        "json_payload": json_payload,
        "created_at": datetime.utcnow().isoformat(),
    }]
    
    errors = client.insert_rows_json(table_id, rows)
    if errors:
        raise Exception(f"BigQuery insert errors: {errors}")
    return True
