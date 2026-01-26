"""GCS storage helper."""
from google.cloud import storage
from shared.config import GCP_PROJECT, GCS_BUCKET

client = storage.Client(project=GCP_PROJECT)
bucket = client.bucket(GCS_BUCKET)


def upload_to_gcs(content: bytes, path: str) -> str:
    """Upload content to GCS and return the full path."""
    blob = bucket.blob(path)
    blob.upload_from_string(content)
    return f"gs://{GCS_BUCKET}/{path}"


def download_from_gcs(path: str) -> bytes:
    """Download content from GCS."""
    if path.startswith("gs://"):
        path = path.replace(f"gs://{GCS_BUCKET}/", "")
    blob = bucket.blob(path)
    return blob.download_as_bytes()
