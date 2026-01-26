# System Architecture Diagram

Copy the code below into [Mermaid Live Editor](https://mermaid.live/) to visualize the system.

## 1. High Level Architecture (ASCII)

```text
       [ USER ]
          |
     (Upload Bill)
          |
          v
+-------------------------------------------------------+
| GOOGLE CLOUD PLATFORM                                 |
|                                                       |
|   [ API Service ] ----> [ Cloud Storage (Raw) ]       |
|         |                                             |
|         v                                             |
|   [ Pub/Sub Queue ]                                   |
|         |                                             |
|         v                                             |
|   [ Worker Service ] <----> [ Gemini AI (LLM) ]       |
|         |                                             |
|         +----> [ PostgreSQL (App DB) ]                |
|         |                                             |
|         +----> [ BigQuery (Analytics) ]               |
|                                                       |
+-------------------------------------------------------+
```

## 2. Mermaid (Simplified)
If you want to try Mermaid again, here is a simpler version without custom styling:

```mermaid
graph LR
    User --> API
    API --> PubSub
    PubSub --> Worker
    Worker --> AI
    Worker --> DB
```

## 2. Sequence Diagram (Detailed Flow)

```mermaid
sequenceDiagram
    autonumber
    actor User
    participant API as FastAPI
    participant GCS as Cloud Storage
    participant PubSub
    participant Worker
    participant LLM as AI Service
    participant DB as PostgreSQL

    User->>API: POST /agent/run (Bill File)
    activate API
    
    API->>GCS: Upload Raw Bill
    API->>PubSub: Publish "INGEST_BILL" Event
    API-->>User: 200 OK (Job ID: Pending)
    deactivate API

    Note over API, Worker: Async Processing (Non-blocking)

    PubSub->>Worker: Consume Message
    activate Worker
    
    Worker->>GCS: Download Bill
    Worker->>LLM: Send Text/Image for Extraction
    LLM-->>Worker: Return JSON (Amount, Dates...)
    
    Worker->>Worker: Validate Data (Pydantic)
    Worker->>DB: Save/Update Bill Record
    
    deactivate Worker
    
    User->>API: GET /agent/result/{job_id}
    API->>DB: Query Status
    DB-->>API: Status: SUCCEEDED
    API-->>User: Return Final Result (JSON)
```
