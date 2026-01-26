# 🎯 Interview Cheat Sheet (Bullet Points)

Mülakat anında ekrana bakıp hızlıca söyleyebileceğin anahtar noktalar:

### 🚀 Projenin Amacı (The Pitch)
*   **İsim:** MiniMeter - AI Destekli Fatura Yönetim Sistemi.
*   **Problem:** Karmaşık faturaların manuel veri girişi hataya açık ve yavaştır.
*   **Çözüm:** LLM kullanarak faturalardan otomatik veri çıkarımı ve analitik raporlama.

### 🏗️ Teknik Mimari (The Tech)
*   **Stack:** Python 3.12, FastAPI, SQLAlchemy, Docker.
*   **Event-Driven:** Google Cloud Pub/Sub kullanarak asenkron bir yapı kurdum.
*   **Serverless:** Google Cloud Run üzerinde otomatik ölçeklenebilir (Scalable) bir yapı.
*   **Data Warehouse:** Operasyonel veri için PostgreSQL, analitik için BigQuery.

### ⚙️ İş Akışı (Detailed Pipeline)
*   **Job Creation:** API isteği alır, DB'de `PENDING` job oluşturur, `job_id` döner (Non-blocking).
*   **Pub/Sub:** Tüm metadata bir JSON mesajı olarak kuyruğa (Queue) push edilir.
*   **Worker:** Mesajı alır, durumu `RUNNING` yapar.
*   **Ingestion:** Connector ile faturayı çeker ve **GCS**'e (`raw/bills/`) yükler.
*   **AI Processing:** GCS'den dosyayı okur, **Gemini (LLM)** ile veriyi çıkartır.
*   **Validation:** LLM çıktısı **Pydantic** modelleri ile doğrulanır.
*   **Persistence:** Veri hem **PostgreSQL**'e (Ops) hem **BigQuery**'ye (Analytics) yazılır.
*   **Finalization:** Job durumu `SUCCEEDED` olarak güncellenir.

### 🛠️ Kritik Özellikler (Key Highlights)
*   **Asenkron Mimari:** Yüksek yük altında sistemin tıkanmasını engeller (Decoupled system).
*   **Secret Management:** Kimlik bilgilerini GCP Secret Manager ile koruyorum.
*   **CI/CD Hazırlığı:** Dockerfile hazır, tek komutla buluta deploy edilebilir.

### 💡 "Neden?" Cevapları
*   **Neden FastAPI?** Pydantic entegrasyonu ve performansı için.
*   **Neden Pub/Sub?** Servisler arası bağımlılığı azaltmak ve hata toleransı için.
*   **Neden BigQuery?** Ham veriden iş değerine (Insights) hızlıca geçmek için.
