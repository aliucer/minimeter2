"""Secret Manager helper."""
from google.cloud import secretmanager
from shared.config import GCP_PROJECT, SECRET_NAME

client = secretmanager.SecretManagerServiceClient()


def get_secret(secret_id: str = SECRET_NAME) -> str:
    """Access a secret from Secret Manager."""
    name = f"projects/{GCP_PROJECT}/secrets/{secret_id}/versions/latest"
    response = client.access_secret_version(request={"name": name})
    return response.payload.data.decode("UTF-8")


def check_secret_access(secret_id: str = SECRET_NAME) -> bool:
    """Check if we can access the secret."""
    try:
        get_secret(secret_id)
        return True
    except Exception:
        return False
