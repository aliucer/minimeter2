# Interview Demo Cheat Sheet

Here are the simple steps to show your project during the interview.

## 1. Preparation (Local)
*   **Terminal**: `cd minimeter2`
*   **Key**: Ensure `psychic-destiny-....json` is present.
*   **Run**: `./run_dev.sh`

## 2. PART 1: Local Demo (Development)
**"First, I'll show the local development environment."**
*   Go to: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
*   Show the **Swagger UI** running locally.
*   Mention: "This runs on my machine using Python/FastAPI."

## 3. PART 2: Cloud Demo (Production)
**"My application is also deployed and live on Google Cloud Run."**

*   Go to: [https://minimeter-api-787646377501.us-central1.run.app/docs](https://minimeter-api-787646377501.us-central1.run.app/docs)
*   Show that it is identical but served from the cloud (look at the URL).
*   **Highlight**: "This is a serverless deployment using Docker and Cloud Run."

## 4. Key Talking Points
*   **Tech Stack**: Python 3.12, FastAPI, SQLAlchemy, Google Cloud (Pub/Sub, BigQuery, Storage).
*   **Architecture**: Event-driven (Async worker processes bills in background).
*   **DevOps**: Dockerized and deployed to Cloud Run.
