"""Shared configuration - loads from .env or environment."""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file
PROJECT_ROOT = Path(__file__).parent.parent
load_dotenv(PROJECT_ROOT / ".env")

# GCP
GCP_PROJECT = os.getenv("GCP_PROJECT")
GCP_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

# Database
DATABASE_URL = os.getenv("DATABASE_URL")

# Pub/Sub
PUBSUB_TOPIC = os.getenv("PUBSUB_TOPIC")
PUBSUB_SUBSCRIPTION = os.getenv("PUBSUB_SUBSCRIPTION")

# GCS
GCS_BUCKET = os.getenv("GCS_BUCKET")

# BigQuery
BQ_DATASET = os.getenv("BQ_DATASET")

# Secret Manager
SECRET_NAME = os.getenv("SECRET_NAME")

# Job settings
MAX_JOB_ATTEMPTS = 3

# Set credentials path for GCP SDK
if GCP_CREDENTIALS:
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(PROJECT_ROOT / GCP_CREDENTIALS)
