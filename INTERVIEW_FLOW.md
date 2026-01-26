# 🎙️ MiniMeter Interview Flow Script

Bu döküman, mülakatta projeyi anlatırken izlemen gereken **hikaye akışını (storyline)** içerir. Senin önerdiğin yapı gayet profesyonel: **Hedef -> Mimari -> Derinlemesine Teknik -> Demo**.

---

## 1. Giriş & Hedef (The "Hook")
*Süre: 2 dakika*

**Sen:** "MiniMeter, enerji faturalarının işlenmesini otomatize eden **yapay zeka destekli bir fatura yönetim sistemidir (AI-powered Utility Bill Management System).**"

*   **Problem:** "Şirketler veya bireyler için elektrik/su faturalarını manuel takip etmek zordur. Veri girişi hataları olur ve analiz yapılamaz."
*   **Çözüm:** "Bu sistem, faturayı (PDF/Resim) alır, AI ile okur, veriyi yapılandırır (normalize eder) ve analitik için saklar."
*   **Hedef:** "Ölçeklenebilir, hataya dayanıklı (fault-tolerant) ve modern bir mimari kurmak."

---

## 2. Mimari & Teknoloji Yığını (The "Stack")
*Süre: 3 dakika*
*(Burada varsa bir diyagram açabilirsin veya sözlü anlatırsın)*

**Sen:** "Projeyi **Microservices** prensiplerine yakın, **Event-Driven (Olay Güdümlü)** bir mimaride tasarladım."

*   **Backend:** Python 3.12 & **FastAPI** (Hızlı ve asenkron olduğu için).
*   **Database:**
    *   **PostgreSQL:** Operasyonel veriler (Kullanıcılar, Faturalar) için.
    *   **BigQuery:** Analitik ve raporlama için (Data Warehouse).
*   **Async Processing:**
    *   API isteği aldığında kullanıcıyı bekletmez, **Google Cloud Pub/Sub**'a bir mesaj atar.
    *   Arka planda çalışan **Worker** servisleri bu mesajı alır ve işler.
*   **Infrastructure:**
    *   Uygulama **Docker**ize edildi.
    *   **Google Cloud Run** üzerinde Serverless olarak çalışıyor (Otomatik ölçekleniyor).

---

## 3. "Nasıl Çalışıyor?" (Detailed Technical Pipeline)
*Süre: 4-5 dakika*

**Sen:** "Sistemin en kritik noktası, asenkron olarak çalışan **End-to-End Processing Pipeline**'dır. İşte bir faturanın sistemdeki yolculuğu:"

1.  **Job Creation (API):**
    *   Kullanıcı `/agent/run` endpoint'ine bir request atar.
    *   API, PostgreSQL üzerinde hemen bir `IngestionJob` kaydı oluşturur (Status: `PENDING`).
    *   Bu aşamada kullanıcıya anında bir `job_id` dönülür (Non-blocking).

2.  **Messaging (Pub/Sub):**
    *   API, gerekli tüm metadata'yı (job_id, account_id, provider) içeren bir JSON mesajını **Google Cloud Pub/Sub**'a push eder.

3.  **Worker Activation:**
    *   Arka planda dinleyen **Worker** servisi mesajı alır.
    *   İlk iş olarak DB'den işin durumunu kontrol eder (**Idempotency check**) ve durumu `RUNNING` olarak günceller.

4.  **Ingestion & Storage (GCS):**
    *   Worker, ilgili `Provider Connector`'ü (Mock veya Real) kullanarak faturayı çeker.
    *   Ham faturayı **Google Cloud Storage (GCS)** üzerine bir `artifact` olarak kaydeder (`raw/bills/{job_id}.txt`).

5.  **AI Extraction (LLM):**
    *   Worker, GCS'den dosyayı okur ve içeriği **Gemini (LLM)** API'sine gönderir.
    *   AI'dan dönen veriyi **Pydantic** modelleriyle doğrular (tutar formatı, tarih geçerliliği vb.).

6.  **Persistence & Analytics (DB & BQ):**
    *   **PostgreSQL:** Operasyonel takip için normalize edilmiş veri buraya yazılır.
    *   **BigQuery:** Analiz ve raporlama için veri aynı anda BigQuery'ye stream edilir.
    *   Son olarak Job status `SUCCEEDED` olarak güncellenir.

**Neden bu kadar detaylı?**
*   **Hata Yönetimi (Retry Logic):** "Eğer LLM veya DB o an erişilemezse, mesaj Pub/Sub'da kalır ve Worker otomatik olarak tekrar dener (Exponential Backoff)."
*   **Ölçeklenebilirlik:** "Aynı anda binlerce fatura gelse bile sistem kilitlenmez, sadece kuyruk (queue) uzar."

---

## 4. Walkthrough / Demo (The "Proof")
*Süre: 5 dakika*

*(Şimdi `DEMO_GUIDE.md` adımlarını uygula)*

1.  **Lokal Demo:**
    *   "Önce lokal ortamımda göstereyim."
    *   Terminal: `./run_dev.sh`
    *   Browser: `localhost:8000/docs`
    *   Swagger'dan `/agent/run` endpoint'ini tetikle.
    *   "Bakın, istek hemen `200 OK` döndü ama işlem arkada devam ediyor (Async)."

2.  **Cloud Demo:**
    *   "Bu sistem şu an production ortamında da canlı."
    *   Link: `https://minimeter-api-....run.app/docs`
    *   "Burası tamamen Google Cloud üzerinde, CI/CD ile deploy edildi."

---

## 5. Kapanış & Sorular
**Sen:** "Özetle; modern bulut teknolojilerini kullanarak, ölçeklenebilir ve dağıtık bir sistem tasarladım. Sorularınız  varsa mimari veya kod bazında detaylandırabilirim."
