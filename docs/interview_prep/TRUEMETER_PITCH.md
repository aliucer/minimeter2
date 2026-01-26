# 🎯 TrueMeter Alignment Pitch

TrueMeter'ın vizyonu: **"Consolidating messy, multi-utility bills into a single and cheaper subscription."**

Senin bu projede kurduğun yapı, tam olarak bu vizyonun **MVP altyapısıdır.** İşte mülakatta kurman gereken bağlantılar:

### 1. "AI Energy Agent" Kavramı
TrueMeter JD'sinde (Job Description) sürekli "AI Energy Agent" ifadesini kullanıyor.
*   **Bağlantı:** Senin projenin `worker/main.py` ve `worker/llm.py` kısmı bu agent'ın beynidir.
*   **Anlatım:** "Geliştirdiğim sistem, ham faturayı okuyup, içindeki veriyi anlamlandıran (reasoning) ve yapılandıran (structuring) bir Energy Agent prototipidir."

### 2. "Messy Data" Sorunu
İlanda "messy, multi-utility bills" deniyor.
*   **Bağlantı:** Projendeki `BillNormalized` Pydantic modeli ve `extract_bill_data` fonksiyonu bu sorunu çözer.
*   **Anlatım:** "Karmaşık fatura formatlarını standart bir veri şemasına (ORM models) dönüştürerek, analitik kararlar alınmasını sağlıyorum."

### 3. "Startup-Ready & Rapid Prototyping"
TrueMeter hıza ve sahiplenmeye (ownership) önem veriyor.
*   **Bağlantı:** Bu projeyi sıfırdan kurup Cloud Run'a kadar canlıya alman senin "execution" gücünü gösterir.
*   **Anlatım:** "Bu projeyi uçtan uca (Python backend'den GCP altyapısına kadar) çok kısa sürede kurguladım ve hemen canlıya alarak (Cloud Run) iterate edilebilir bir MVP oluşturdum."

### 4. Teknik Eşleşme (Technical Match)
| JD Gereksinimi | Senin Projendeki Karşılığı |
| :--- | :--- |
| **LLM-driven systems** | Gemini AI (LLM) entegrasyonu ve Prompt Engineering. |
| **Orchestrate data pipelines** | Pub/Sub + Worker + BigQuery akışı. |
| **Microservices in Python** | FastAPI tabanlı bağımsız servis mimarisi. |
| **Reliable connectors** | `worker/connectors` klasöründeki extensible yapı. |
| **CI/CD, logs, metrics** | `Dockerfile`, `run_dev.sh` ve yapılandırılmış logging. |

### 💡 "Final Punch" (Kapanış Cümlesi)
"TrueMeter'ın enerji faturalarını birer finansal varlık gibi yönetme vizyonu beni heyecanlandırıyor. Bu projede kurduğum asenkron ve AI-native mimari, binlerce faturayı saniyeler içinde işleyebilecek kadar ölçeklenebilir; tam da TrueMeter'ın ölçeklenme hedefleriyle örtüşüyor."
