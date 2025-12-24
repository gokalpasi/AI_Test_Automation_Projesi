import google.generativeai as genai
import os
import time
from dotenv import load_dotenv

# .env dosyasındaki çevresel değişkenleri (API anahtarları vb.) sisteme yükler
load_dotenv()


def get_all_api_keys():
    """
    Sistemdeki tüm Gemini API anahtarlarını toplar.
    'GEMINI_API_KEY_1', 'GEMINI_API_KEY_2' gibi sıralı anahtarları ve
    varsayılan 'GEMINI_API_KEY'i bir liste halinde döndürür.
    """
    keys = []
    i = 1
    # Dinamik olarak GEMINI_API_KEY_n formatındaki tüm anahtarları tara
    while True:
        key = os.getenv(f"GEMINI_API_KEY_{i}")
        if key:
            keys.append(key)
            i += 1
        else:
            break

    # Eğer varsa, tekil/fallback API anahtarını da listeye ekle (mükerrer kontrolü ile)
    fallback = os.getenv("GEMINI_API_KEY")
    if fallback and fallback not in keys:
        keys.append(fallback)

    if not keys:
        return []

    return keys


def generate_test_code_from_gemini(user_prompt, fix_for_streamlit=False, mode="general"):
    """
    Belirlenen moda göre (Genel Test veya Spesifik Test Case) Gemini AI modelinden
    Python unittest kodu üretir. API kota sınırlarını aşmak için anahtar rotasyonu uygular.

    Args:
        user_prompt (str): Test edilecek kod veya test senaryosu.
        fix_for_streamlit (bool): Kodun Streamlit ortamında çalışması için gerekli main bloğunu ekler.
        mode (str): Prompt stratejisi seçimi ("general" veya "test_case").
    """

    api_keys = get_all_api_keys()

    if not api_keys:
        return "Hata: Hiçbir API Key bulunamadı. .env dosyasını kontrol edin."

    # --- PROMPT MÜHENDİSLİĞİ (Prompt Engineering) ---

    # Strateji 1: Genel amaçlı, kaynak koddan test üreten sistem talimatı
    prompt_general = """
    Sen uzman bir yazılım test mühendisisin. 
    Aşağıda verilen senaryoyu analiz et ve profesyonel bir 'unittest' kodu yaz.

    KURALLAR:
    1. Sadece Python kodu ver. Açıklama yapma.
    2. Kod bloklarını ```python etiketi içine al.
    3. Test edilecek fonksiyonları 'app' modülünden import et. (from app import ...)
    4. Fonksiyonları testin içinde tekrar tanımlama, import et.
    """

    # Strateji 2: Adım adım Test Case dökümanından kod üreten sistem talimatı
    prompt_test_case = """
    Sen uzman bir Test Otomasyon Mühendisisin.
    Görevin: Sana verilen yapılandırılmış "Test Case" (Test Durumu) metnini analiz etmek ve buna karşılık gelen Python 'unittest' kodunu yazmaktır.

    GİRDİ FORMATI (TEST CASE):
    Genellikle şu bilgileri içerir: Test ID, Tanım, Ön Koşullar, Test Adımları, Beklenen Sonuç.

    KURALLAR:
    1. Sadece Python kodu ver. Açıklama, markdown veya ekstra metin yazma.
    2. Kod bloklarını ```python etiketi içine al.
    3. Test edilecek fonksiyonları temsili olarak 'app' modülünden import et (from app import ...).
    4. Test Case içindeki her bir adımı kod içinde yorum satırı (# Adım 1: ...) olarak belirt.
    5. "Beklenen Sonuç" kısmını mutlaka 'assert' ifadeleriyle doğrula (self.assertEqual, assertTrue vb.).
    """

    # Çalışma moduna göre ilgili sistem talimatını (system instruction) belirle
    if mode == "test_case":
        system_instruction = prompt_test_case
    else:
        system_instruction = prompt_general

    # Streamlit (Web Arayüzü) uyumluluğu için unittest execution bloğunu enjekte et
    if fix_for_streamlit:
        system_instruction += """
        ÇOK ÖNEMLİ TEKNİK KURAL:
        Kodun en altına MUTLAKA şu bloğu ekle:
        if __name__ == '__main__':
            import unittest
            unittest.main(argv=['first-arg-is-ignored'], exit=False)
        """

    # Sistem talimatı ile kullanıcı girdisini birleştirerek tam promptu oluştur
    full_prompt = f"{system_instruction}\n\nKullanıcı Girdisi:\n{user_prompt}"

    # AI Güvenlik Ayarları: Üretilen kodun filtre takılmaması için kısıtlamaları esnet
    safety_settings = [
        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
    ]

    # --- API KEY ROTASYON VE HATA YÖNETİMİ ---
    # Toplam anahtar sayısının 3 katı kadar deneme yaparak geçici hataları tolere et
    max_attempts = len(api_keys) * 3

    for attempt in range(max_attempts):
        # Modülo aritmetiği ile sıradaki API anahtarını seç (Round-robin)
        current_key_index = attempt % len(api_keys)
        current_key = api_keys[current_key_index]

        try:
            # Seçili anahtar ile Gemini modelini yapılandır
            genai.configure(api_key=current_key)
            model = genai.GenerativeModel('gemini-flash-latest')

            # İçerik üretimi isteğini gönder
            response = model.generate_content(full_prompt, safety_settings=safety_settings)

            # Yanıtın boş gelip gelmediğini veya filtreye takılıp takılmadığını kontrol et
            if not response.parts:
                if hasattr(response, 'prompt_feedback'):
                    return f"AI cevap veremedi. Filtre: {response.prompt_feedback}"
                return "AI boş cevap döndürdü."

            # Markdown etiketlerini temizle ve saf Python kodunu dışarı aktar
            cleaned_code = response.text.replace("```python", "").replace("```", "").strip()
            return cleaned_code

        except Exception as e:
            error_msg = str(e)
            # HTTP 429: Too Many Requests (Kota Aşımı) hatası durumunda anahtar değiştir
            if "429" in error_msg or "quota" in error_msg.lower():
                print(f"⚠️ Anahtar {current_key_index + 1} kotası doldu! Sıradaki anahtara geçiliyor... (Hata: 429)")
                time.sleep(1)  # API limitlerini zorlamamak için kısa mola
                continue
            else:
                # Kota harici kritik hataları (bağlantı vb.) hemen raporla
                return f"Beklenmeyen Hata: {error_msg}"

    return "Hata: Tüm API anahtarlarının kotası dolu! Biraz bekleyiniz..."