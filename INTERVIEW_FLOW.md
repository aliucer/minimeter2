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

## 3. "Nasıl Çalışıyor?" (The "Deep Dive")
*Süre: 3 dakika*
*(Burada teknik derinliğini göstereceksin)*

**Sen:** "Sistemin en kritik noktası **Asenkron İşleme Hattı (Pipeline)**."

1.  **Ingestion (Veri Alımı):** Kullanıcı faturayı yükler. API bunu Cloud Storage'a (GCS) kaydeder ve Pub/Sub'a `INGEST_BILL` eventi atar.
2.  **Processing (İşleme):** Worker, bu eventi yakalar. Dosyayı indirir ve **LLM (Large Language Model)** servisine gönderir.
3.  **Normalization:** LLM'den dönen ham veri (JSON), Pydantic modelleri ile doğrulanır (Validation). Eksik alan varsa `fallback` mekanizmaları devreye girer.
4.  **Storage:** Temiz veri hem PostgreSQL'e hem de BigQuery'ye yazılır.

**Neden böyle yaptım?**
*   "API'yi bloklamamak (Non-blocking) için."
*   "Yüksek trafik gelirse Queue (Kuyruk) mekanizması sayesinde sistem çökmez, yavaş yavaş işler (Backpressure)."

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
