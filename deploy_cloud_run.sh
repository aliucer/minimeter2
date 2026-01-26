#!/bin/bash

# Configuration
SERVICE_NAME="minimeter2-api"
REGION="us-central1"
PROJECT_ID="psychic-destiny-485404-q6"

echo ">>> Enabling required services..."
gcloud services enable run.googleapis.com cloudbuild.googleapis.com artifactregistry.googleapis.com --project $PROJECT_ID

echo ">>> Deploying to Cloud Run..."
# We pass the env vars explicitly from the .env file values we know
gcloud run deploy $SERVICE_NAME \
  --source . \
  --project $PROJECT_ID \
  --region $REGION \
  --allow-unauthenticated \
  --set-env-vars GCP_PROJECT=$PROJECT_ID \
  --set-env-vars DATABASE_URL="postgresql://postgres:demo123@34.28.82.253:5432/truemeter_demo" \
  --set-env-vars PUBSUB_TOPIC="ingestion-jobs" \
  --set-env-vars PUBSUB_SUBSCRIPTION="ingestion-jobs-sub" \
  --set-env-vars GCS_BUCKET="minimeter-raw-data" \
  --set-env-vars BQ_DATASET="truemeter_demo" \
  --set-env-vars SECRET_NAME="utility-demo-credentials" \
  --set-env-vars GOOGLE_APPLICATION_CREDENTIALS="/app/psychic-destiny-485404-q6-6f7e6c295fc6.json"
