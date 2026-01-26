# MiniMeter Code Walkthrough - Mülakat Hazırlık

Bu doküman kodun her parçasını adım adım açıklar. Mülakatta sorulabilecek sorulara hazırlık için kullan.

---

## 1. Proje Yapısı

```
minimeter2/
├── shared/         # Ortak modüller (her iki servis kullanır)
├── api/            # REST API (FastAPI)
├── worker/         # Async job processor
└── eval/           # LLM test suite
```

**Neden bu yapı?**
- `shared/` → DRY principle, config ve schema'lar tek yerde
- `api/` ve `worker/` ayrı → Bağımsız deploy edilebilir microservices

---

## 2. shared/ - Ortak Modüller

### 2.1 config.py
```python
GCP_PROJECT = os.getenv("GCP_PROJECT", "psychic-destiny-485404-q6")
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://...")
```
**Neden?** Tüm env variables tek yerde. Production'da env ile override edilir.

### 2.2 database.py
```python
@contextmanager
def get_db():
    session = SessionLocal()
    try:
        yield session
        session.commit()
    finally:
        session.close()
```
**Neden context manager?** 
- Auto-commit on success
- Auto-rollback on error
- Connection leak prevention

### 2.3 schemas.py
```python
class BillNormalized(BaseModel):
    billing_period_start: date
    billing_period_end: date
    total_amount: float
    line_items: List[LineItem]
```
**Neden Pydantic?**
- LLM output validation
- Type safety
- Auto JSON serialization

---

## 3. api/ - REST API

### 3.1 main.py - Endpoint'ler

**Health check:**
```python
@app.get("/health")
def health():
    return {"ok": True}
```
Load balancer ve monitoring için.

**Agent endpoint (en önemli):**
```python
@app.post("/agent/run")
def agent_run(utility_account_id: int, db: Session = Depends(get_db_dependency)):
    # 1. Utility account kontrol
    account = db.query(UtilityAccount).filter(...).first()
    
    # 2. Job oluştur
    job = IngestionJob(job_type="FULL_PIPELINE", status="PENDING")
    db.add(job)
    db.commit()
    
    # 3. Pub/Sub'a publish
    publish_job(job.id, utility_account_id, "FULL_PIPELINE")
    
    return {"job_id": job.id, "message": "Poll /agent/result/..."}
```

**Neden async değil de Pub/Sub?**
- API hızlı response verir
- Heavy work (LLM) arka planda yapılır
- Retry ve error handling Pub/Sub tarafında

### 3.2 models.py - SQLAlchemy ORM
```python
class IngestionJob(Base):
    __tablename__ = "ingestion_jobs"
    id = Column(Integer, primary_key=True)
    status = Column(String)  # PENDING, RUNNING, SUCCEEDED, FAILED
    error_message = Column(String)
    attempt_count = Column(Integer)
```
**Neden bu alanlar?**
- `status` → Job lifecycle tracking
- `error_message` → Debug için
- `attempt_count` → Retry limit kontrolü

### 3.3 pubsub.py
```python
def publish_job(job_id, utility_account_id, job_type, customer_id=None):
    message = {"job_id": job_id, "utility_account_id": utility_account_id, ...}
    publisher.publish(topic_path, json.dumps(message).encode())
```
**Neden JSON?** Pub/Sub bytes alır, JSON human-readable ve debug kolay.

---

## 4. worker/ - Job Processor

### 4.1 main.py - Ana Akış

```python
def handle_message(message):
    # 1. Parse message
    data = json.loads(message.data)
    job_id = data["job_id"]
    
    # 2. Idempotency check
    if job_info["status"] == "SUCCEEDED":
        message.ack()  # Zaten işlendi
        return
    
    # 3. Retry limit
    if job_info["attempt_count"] >= 3:
        update_job(job_id, "FAILED", "Exceeded retry limit")
        message.ack()
        return
    
    # 4. Process
    update_job(job_id, "RUNNING", increment_attempt=True)
    process_full_pipeline(job_id, utility_account_id, customer_id, provider)
    update_job(job_id, "SUCCEEDED")
    
    message.ack()
```

**Neden ack/nack?**
- `ack()` → Mesaj işlendi, kuyruktan sil
- `nack()` → İşlenemedi, tekrar dene (Pub/Sub redelivery)

### 4.2 connectors/ - Tool Selection

```python
# registry.py
CONNECTOR_REGISTRY = {
    "MOCK_A": MockUtilityAConnector,
    "MOCK_B": MockUtilityBConnector,
}

def get_connector(provider):
    return CONNECTOR_REGISTRY.get(provider, MockUtilityAConnector)()
```

**Neden registry pattern?**
- Yeni provider = yeni class, tek satır registry'ye ekle
- Open/Closed principle
- Mülakatta "LLM + Tools" pattern olarak anlat

### 4.3 llm.py - LLM Extraction

```python
def extract_bill_data(bill_text, provider=None):
    prompt = EXTRACTION_PROMPT
    if provider:
        prompt += f"\nProvider: {provider}\n"  # Context
    prompt += "\nBill text:\n" + bill_text
    
    response = model.generate_content(prompt)
    return json.loads(response.text)
```

**Neden provider context?**
- Farklı provider'lar farklı format kullanır
- LLM'e "bu PG&E formatı" demek accuracy artırır

### 4.4 storage.py - GCS

```python
def upload_to_gcs(content, path):
    blob = bucket.blob(path)
    blob.upload_from_string(content)
    return f"gs://{GCS_BUCKET}/{path}"
```

**Neden GCS?**
- Raw bill'leri sakla (audit trail)
- Reprocessing için
- LLM debug için

### 4.5 bigquery.py - Analytics

```python
def insert_normalized_bill(...):
    rows = [{"customer_id": ..., "total_amount": ..., ...}]
    client.insert_rows_json(table_id, rows)
```

**Neden hem SQL hem BigQuery?**
- SQL: Transactional, job status, customer data
- BigQuery: Analytics, aggregation, reporting

---

## 5. Data Flow - Tam Akış

```
1. POST /agent/run {utility_account_id: 1}
   ↓
2. API: Job oluştur (PENDING), Pub/Sub'a publish
   ↓
3. Worker: Mesajı al, idempotency check
   ↓
4. Worker: Provider'a göre connector seç (registry)
   ↓
5. Connector: Bill text'i al (mock veri)
   ↓
6. Worker: GCS'e upload (artifact)
   ↓
7. Worker: LLM'e gönder (Gemini), provider context ile
   ↓
8. Worker: Pydantic ile validate (BillNormalized)
   ↓
9. Worker: SQL'e kaydet, BigQuery'ye kaydet
   ↓
10. Worker: Job status = SUCCEEDED, ack()
```

---

## 6. Scaling Noktaları (Soru gelirse)

| Bileşen | Şimdi | 10K'da |
|---------|-------|--------|
| LLM | Her call ~2sn | Cache + rate limit |
| Worker | Tek process | Cloud Run Jobs paralel |
| DB | Her request connection | Connection pooling |
| Pub/Sub | Sync | Batch + async |

---

## 7. Mülakat Cümleleri

**Mimari:**
> "Async job processing için Pub/Sub kullandım. API hızlı response verir, heavy work arka planda yapılır."

**LLM:**
> "LLM output'unu Pydantic ile validate ediyorum. Schema violation olursa job FAILED olur, debug için error log kalır."

**Scale:**
> "Worker'lar stateless, horizontal scale kolay. LLM bottleneck için cache layer eklenirdi."

**Connector:**
> "Registry pattern ile yeni provider eklemek tek class. Open/Closed principle."

---

## 8. Sık Sorulabilecek Sorular

**S: Neden Pub/Sub, neden Celery değil?**
C: GCP-native, managed, retry built-in, Cloud Run ile iyi entegre.

**S: LLM hallucination olursa?**
C: Pydantic validation yakalar. Fallback olarak regex var. Eval set ile accuracy ölçüyorum.

**S: Gerçek connector nasıl olurdu?**
C: Aynı interface, login + scraping + PDF parse. Pattern aynı kalır.

**S: Neden BigQuery + SQL ikisi de?**
C: SQL transactional (job status), BigQuery analytics (aggregation).

---

## 9. GCP Servisleri - Savunma Rehberi

Her servis için "Neden bunu seçtin?" sorusuna verilecek cevaplar:

### 1. Cloud Pub/Sub (Async Messaging)
**Neden:** API ve Worker'ı birbirinden koparmak (decouple) için.
**Nasıl Açıklarsın:**
> "API request'ini bloklamadan ağır işlemleri (LLM extraction) yapmak için async bir yapı kurmam gerekiyordu. Pub/Sub, built-in retry mekanizması ve 'at-least-once' delivery garantisi verdiği için RabbitMQ gibi sistemleri yönetmek yerine bu managed servisi seçtim. Ayrıca Worker sayısı arttırılarak kolayca scale olabiliyor."

### 2. Google Cloud Storage (GCS) (Object Storage)
**Neden:** Yapısal olmayan (unstructured) raw bill verisini saklamak için.
**Nasıl Açıklarsın:**
> "Veritabanları binary dosya veya büyük text blokları saklamak için pahalı ve verimsiz. Raw fatura metinlerini (veya ileride PDF'leri) GCS'te 'raw/bills/{job_id}.txt' olarak saklıyorum. Bu hem ucuz, hem de LLM extraction'ı debug etmek veya ileride daha iyi bir modelle tekrar process etmek (re-drive) için orijinal veriyi korumamı sağlıyor."

### 3. BigQuery (Data Warehouse)
**Neden:** Analitik sorgular ve raporlama için.
**Nasıl Açıklarsın:**
> "Cloud SQL (PostgreSQL) operasyonel veriler (User, Job Status) için mükemmel ama, 'Geçen yılın enerji tüketim trendi nedir?' gibi ağır analitik sorgular production veritabanını yorar. Normalized veriyi BigQuery'ye atarak operasyonel yük ile analitik yükü ayırdım (Separation of Concerns). Ayrıca BigQuery columanr storage olduğu için bu tip aggregation'larda çok daha hızlı."

### 4. Secret Manager
**Neden:** Hassas verileri (API Keyleri, DB şifreleri) koddan uzak tutmak için.
**Nasıl Açıklarsın:**
> "Mülakat projesi olsa bile security best practice'lerine uymak istedim. `.env` dosyaları productionda riskli olabilir. Secret Manager ile credential'ları kod repository'sinden tamamen ayırdım ve access control (IAM) ile sadece uygulamanın erişmesini sağladım."

### 5. Cloud Run (Serverless Compute)
**Neden:** Altyapı yönetmeden container çalıştırmak için.
**Nasıl Açıklarsın:**
> "Bir start-up ortamında Ops işlerine (K8s cluster yönetimi, sunucu güncelleme) vakit harcamak yerine koda odaklanmak istedim. Cloud Run, container'ımı alıp trafiğe göre otomatik scale ediyor (0'dan N'e). HTTP request gelmediğinde scale-to-zero özelliği sayesinde maliyeti de düşürüyor."
