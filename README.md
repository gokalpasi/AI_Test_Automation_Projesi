# 🤖 AI-Powered Auto Test Agent (Otonom Test Aracı)

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Gemini API](https://img.shields.io/badge/AI-Gemini%20Pro-orange)
![Streamlit](https://img.shields.io/badge/Frontend-Streamlit-red)
![Status](https://img.shields.io/badge/Status-Stable-success)

Bu proje, Python kodları için **otomatik unit test yazan, çalıştıran ve hataları kendi kendine düzelten (Self-Healing)** yapay zeka destekli bir otomasyon aracıdır.

Google Gemini API kullanılarak geliştirilen ajan, Reinforcement Learning (RL) prensiplerine benzer bir geri bildirim döngüsüyle çalışır.

## 🚀 Özellikler

Proje 3 ana modülden oluşur:

* **Modül 1: Kod Üretimi & Statik Analiz**
    * Doğal dildeki senaryoları (örn: "Kargo hesaplama testi") Python test koduna çevirir.
    * Üretilen kodun karmaşıklığını (Radon Complexity) ve kalitesini ölçer.
    * **Call Graph:** Kodun çalışma mantığını görselleştiren akış şemaları çizer.

* **Modül 2: Test Coverage (Kapsama) Analizi**
    * Mevcut kaynak kodunuz ve test kodunuzu yükleyip "Kodun yüzde kaçı test edildi?" sorusuna yanıt verir.
    * Test edilmeyen satırları kod üzerinde kırmızı ile işaretler.

* **Modül 3: Otonom Ajan (Auto-Test Agent)** 🔥 *En Güçlü Modül*
    * Sadece kaynak kodu verirsiniz.
    * Ajan testi yazar, çalıştırır ve **Coverage oranını** ölçer.
    * Eğer hata alırsa veya Coverage düşükse, hatayı okur ve **kendi yazdığı kodu düzelterek** tekrar dener.
    * %100 Kapsama oranına ulaşana kadar (veya max deneme sayısına kadar) döngü devam eder.

## 🛠️ Kurulum

Projeyi yerel ortamınızda çalıştırmak için:

1.  **Repoyu Klonlayın:**
    ```bash
    git clone [https://github.com/kullaniciadi/ai-test-agent.git](https://github.com/kullaniciadi/ai-test-agent.git)
    cd ai-test-agent
    ```

2.  **Sanal Ortam Oluşturun (Önerilen):**
    ```bash
    python -m venv venv
    # Windows:
    venv\Scripts\activate
    # Mac/Linux:
    source venv/bin/activate
    ```

3.  **Gerekli Kütüphaneleri Yükleyin:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **API Anahtarını Ayarlayın:**
    Ana dizinde `.env` dosyası oluşturun ve Gemini API anahtarınızı ekleyin:
    ```env
    GEMINI_API_KEY=senin_api_anahtarin_burada
    ```

## ▶️ Kullanım

Uygulamayı başlatmak için terminale şu komutu girin:

```bash
streamlit run main.py

AI_TEST_AUTOMATION_PROJESI/
│
├── modules/                  # Çekirdek Modüller
│   ├── ai_generator.py       # LLM (Gemini) Bağlantısı
│   ├── coverage_tool.py      # Test Çalıştırma ve Coverage Ölçümü
│   ├── metrics.py            # Radon Karmaşıklık Analizi
│   ├── visualizer.py         # Call Graph Görselleştirme
│   └── agent.py              # Otonom Ajan (RL Döngüsü)
│
├── temp_files/               # Geçici test dosyalarının oluşturulduğu yer
├── main.py                   # Streamlit Ana Arayüzü
├── requirements.txt          # Bağımlılıklar
└── .env                      # API Anahtarı

