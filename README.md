# 🤖 RL & LLM Destekli Otomatik Test Üreticisi (Auto-Test-Agent)

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Gemini API](https://img.shields.io/badge/LLM-Gemini%20Pro-orange)
![Reinforcement Learning](https://img.shields.io/badge/AI-Reinforcement%20Learning-red)
![Status](https://img.shields.io/badge/Status-Completed-success)

Bu proje, **Reinforcement Learning (Pekiştirmeli Öğrenme)** ve **Google Gemini API** kullanarak Python kodları için otomatik olarak yüksek kaliteli unit testler (birim testleri) üreten akıllı bir ajandır.

Agent, üretilen test kodunun kalitesini (**Cyclomatic Complexity** ve kapsam) analiz eder ve bu metrikleri bir "ödül" (reward) mekanizması olarak kullanarak zamanla daha iyi testler yazmayı öğrenir.

## 🚀 Projenin Amacı

Geleneksel test yazma süreçlerini otomatize etmek ve LLM'lerin rastgele çıktı üretme potansiyelini, matematiksel bir kalite metriği (Radon Complexity) ile denetleyerek optimize etmektir.

## ⚙️ Özellikler

* **🧠 LLM Entegrasyonu:** Google Gemini Pro modeli ile doğal dil işleme ve kod üretimi.
* **🎮 Reinforcement Learning Döngüsü:**
    * **State (Durum):** Mevcut kodun ve testin durumu.
    * **Action (Eylem):** Prompt stratejisini değiştirme veya iyileştirme.
    * **Reward (Ödül):** Düşük karmaşıklık (complexity) ve hatasız çalışma durumunda pozitif ödül.
* **📊 Kod Analizi:** `Radon` kütüphanesi ile üretilen kodun Siklomatik Karmaşıklığının hesaplanması.
* **🔄 Kendi Kendini İyileştirme:** Hatalı test durumlarında agent'ın cezalandırılması ve strateji değiştirmesi.

## 🛠️ Kurulum

Projeyi yerel ortamınızda çalıştırmak için aşağıdaki adımları izleyin.

### 1. Repoyu Klonlayın
```bash
git clone [https://github.com/kullaniciadi/proje-adi.git](https://github.com/kullaniciadi/proje-adi.git)
cd proje-adi

#Sanal Ortam (Virtual Environment) Oluşturun
python -m venv venv
# Windows için:
venv\Scripts\activate
# Mac/Linux için:
source venv/bin/activate


#Gerekli Kütüphaneleri Yükleyin
pip install -r requirements.txt


#Ortam Değişkenlerini Ayarlayın
#Proje dizininde bir .env dosyası oluşturun ve Google API anahtarınızı ekleyin:
GEMINI_API_KEY=senin_api_anahtarin_buraya

#Uygulamayı başlatmak için ana scripti çalıştırın:
streamlit run main.py
