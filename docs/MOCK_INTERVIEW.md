# 🎙️ Mock Interview Drill

Bu dosya, mülakat simülasyonu için hazırlanmıştır. Kendine bu soruları sor ve cevapları sesli olarak çalış.

---

## 🟢 Seviye 1: Isınma & Davranışsal

**Soru 1:** "Neden Cloud Run Jobs değil de sürekli çalışan bir Worker servisi tasarladın?"
**Cevap:**
> "Başlangıç için latency'yi düşük tutmak istedim. Cloud Run Jobs'un başlatma süresi (cold start) anlık fatura yüklemelerinde kullanıcıyı bekletebilirdi. Sürekli çalışan bir worker (Pub/Sub pull subscription ile), mesaj gelir gelmez işlemeye başlıyor. Ancak maliyet optimizasyonu gerekirse ve yük tahmin edilebilir aralıklarla geliyorsa (batch), Cloud Run Jobs'a geçmek trivial bir değişiklik olur."

**Soru 2:** "Projeyi geliştirirken karşılaştığın en zor teknik problem neydi?"
**Cevap:**
> "LLM'in halüsinasyon görme ihtimaliydi. Başlangıçta GEMINI bazen JSON yerine markdown döndürüyordu veya tarihleri yanlış formatlıyordu.
> Çözmek için iki katmanlı bir yapı kurdum:
> 1. **Prompt Engineering:** Provider context'i (bu PG&E faturasıdır) vererek modelin odağını daralttım.
> 2. **Strict Validation:** Pydantic kullanarak çıktıyı zorladım. Validasyon geçmezse retry mekanizması devreye giriyor.
> Ayrıca regex fallback ekleyerek, LLM tamamen saçmalasa bile en azından 'Toplam Tutar'ı kurtarmayı garantiye aldım."

---

## 🟡 Seviye 2: Mimari & Sistem Tasarımı

**Soru 3:** "Sisteminde API çökerse ne olur? Worker çökerse ne olur?"
**Cevap:**
> "API çökerse (Cloud Run instance fail olursa), Cloud Run otomatik olarak yeni bir instance kaldırır. Stateless olduğu için veri kaybı olmaz, sadece o anki requestler fail eder (Client retry yapmalı).
>
> Worker çökerse, Pub/Sub'ın 'At-least-once delivery' garantisi devreye girer. Worker mesajı işlemeyi bitirip `ack()` göndermediği sürece, Pub/Sub o mesajı bekletir ve belirli bir süre sonra (ack deadline) tekrar kuyruğa koyar. Başka bir worker (veya yeniden ayağa kalkan worker) o mesajı alıp kaldığı yerden devam eder. Veri kaybı olmaz."

**Soru 4:** "Database olarak neden PostgreSQL (Cloud SQL) seçtin de NoSQL (Firestore vs) seçmedin?"
**Cevap:**
> "Veri modelim ilişkisel. `Customer` -> `UtilityAccount` -> `IngestionJob` arasında net bir hiyerarşi ve ilişki var. Tutarlılık (Consistency) benim için önemliydi; bir job oluşturulduğunda account'un var olduğundan emin olmak istedim (Foreign Key constraints). NoSQL ile bu ilişkileri yönetmek kod tarafında ekstra yük getirecekti."

---

## 🔴 Seviye 3: Deep Dive & Python

**Soru 5:** "Python'da `async/await` kullanmak yerine neden Threading veya Multiprocessing kullanmadın?"
**Cevap:**
> "Bu proje I/O bound bir iş yapıyor (Network çağrıları: GCS upload, Gemini API, DB write). CPU tarafında ağır bir hesaplama yapmıyoruz.
> Python'da I/O bound işler için `asyncio` veya thread tabanlı concurrency en verimli yöntemdir. Worker tarafında Google Pub/Sub kütüphanesi zaten arka planda thread havuzu kullanarak mesajları asenkron çekiyor. Eğer CPU-heavy bir iş (örn: local OCR) yapsaydım Multiprocessing düşünürdüm."

**Soru 6:** "Worker kodunda `db.query(Job)` yapıp güncelliyorsun. Ya iki worker aynı anda aynı job'ı güncellemeye çalışırsa (Race Condition)?"
**Cevap:**
> "Güzel soru. Şu anki tasarımda her `job_id` için Pub/Sub'a tek bir mesaj atılıyor, dolayısıyla normal şartlarda iki worker aynı job'a dokunmaz.
> Ancak, Pub/Sub nadiren de olsa aynı mesajı iki kere teslim edebilir (duplicate delivery). Bunu çözmek için `handle_message` içinde ilk iş olarak DB'den job statüsünü kontrol ediyorum. Eğer `SUCCEEDED` ise işlem yapmadan çıkıyorum (Idempotency).
> Daha kritik bir race condition olsaydı, SQL tarafında `SELECT ... FOR UPDATE` kullanarak satırı kilitlerdim."

---

## 🧪 Bonus: "Bize kodu bozan bir senaryo söyle?"

**Soru:** "Sistemi nasıl çökertirsin?"
**Cevap:**
> "Eğer bir kullanıcı 100MB boyutunda binary bir dosya (veya bozuk bir zip) yüklerse, Worker bunu belleğe (RAM) almaya çalışırken `MemoryError` verip çökertebilirim.
> Çözüm: GCS'den dosya indirirken chunk-based (parça parça) okuma yapmak ve dosya boyutu limiti koymak."
wwww