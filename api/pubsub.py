"""Pub/Sub publisher helper."""
import json
from google.cloud import pubsub_v1
from shared.config import GCP_PROJECT, PUBSUB_TOPIC

publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(GCP_PROJECT, PUBSUB_TOPIC)


def publish_job(job_id: int, utility_account_id: int, job_type: str, customer_id: int = None) -> str:
    """Publish a job message to Pub/Sub."""
    message = {
        "job_id": job_id,
        "utility_account_id": utility_account_id,
        "job_type": job_type,
    }
    if customer_id is not None:
        message["customer_id"] = customer_id
    
    data = json.dumps(message).encode("utf-8")
    future = publisher.publish(topic_path, data)
    return future.result()
