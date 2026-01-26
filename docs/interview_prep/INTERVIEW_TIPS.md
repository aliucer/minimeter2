# 💡 Interview Golden Rules & Tips

Mülakatta fark yaratmanı sağlayacak, "teknik derinliği" olan kritik noktalar:

## 1. "Neden?" Sorusuna Hazır Ol
Sana muhtemelen "Neden Pub/Sub kullandın, doğrudan Worker'a istek atsaydın ya?" diyecekler.
*   **Cevabın:** "Sistemi **Decouple** etmek (birbirinden ayırmak) için. Eğer 1000 fatura birden gelirse, API çökmez; Pub/Sub bu yükü biriktirir (Buffer) ve Worker'lar kendi hızında güvenle işler. Bu sistemin **Scalability** ve **Fault-Tolerance** (hataya dayanıklılık) kapasitesini artırır."

## 2. Güvenliği Vurgula
"Hassas verileri nasıl koruyorsun?"
*   **Cevabın:** "Google Cloud **Secret Manager** kullanıyorum. Kimlik bilgilerini (API keys, DB passwords) asla kodun içinde saklamıyorum. Ayrıca `.gitignore` dosyam çok sıkı; GCP key dosyalarını yanlışlıkla bile GitHub'a yüklememi engelliyor."

## 3. "Analitik Bakış Açısı" (BigQuery)
Sadece fatura işlemek yetmez, veriyle ne yapılıyor?
*   **Cevabın:** "Veriyi sadece PostgreSQL'e (transactional) değil, aynı zamanda **BigQuery**'ye (analytical) de atıyorum. Bu sayede ileride büyük veri analizi, trend takibi ve maliyet projeksiyonları yapılabilir hale geliyor."

## 4. Unutma! (Demo Öncesi Check)
*   [ ] **JSON Key:** Mac'inde proje klasöründe `psychic-destiny-....json` dosyasının olduğundan emin ol.
*   [ ] **Local Env:** Demo başlamadan önce `./run_dev.sh` yapıp terminali hazır tut.
*   [ ] **Worker:** Lokal demo yapacaksan `python -m worker.main` komutunun ayrı bir terminalde çalıştığından emin ol.
*   [ ] **Cloud Run:** İnternetin yavaşsa lokal yerine direkt Cloud Run linkini (Swagger) göstererek başla, zaman kaybetme.

## 5. Bonus: "Neyi Geliştirirsin?" Sorusu
"Vaktin olsa neyi daha iyi yapardın?"
*   **Cevabın:** "Sisteme **Monitoring** (Prometheus/Grafana) ve daha kapsamlı **Unit Test**'ler eklerdim. Ayrıca faturaları işlerken **Human-in-the-loop** (yani AI emin olamadığında bir insanın onayına düşme) mekanizması kurardım."
