import google.generativeai as genai
import os
import time
from dotenv import load_dotenv

# Ortam değişkenlerini yükle
load_dotenv()

def get_all_api_keys():
    """
    API Key listesini döndürür.
    """
    keys = []
    i = 1
    while True:
        key = os.getenv(f"GEMINI_API_KEY_{i}")
        if key:
            keys.append(key)
            i += 1
        else:
            break
            
    fallback = os.getenv("GEMINI_API_KEY")
    if fallback and fallback not in keys:
        keys.append(fallback)
    
    if not keys:
        return []
    
    # print(f"ℹ️ Sistemde {len(keys)} adet API Anahtarı bulundu. Rotasyon aktif.") # İstersen yorum satırı yapabilirsin
    return keys

def generate_test_code_from_gemini(user_prompt, fix_for_streamlit=False, mode="general"):
    """
    mode: "general" (Eski Prompt) veya "test_case" (Yeni Test Case Promptu)
    """
    
    api_keys = get_all_api_keys()
    
    if not api_keys:
        return "Hata: Hiçbir API Key bulunamadı. .env dosyasını kontrol edin."

    # --- PROMPT SEÇİM MANTIĞI ---
    
    # 1. ESKİ PROMPT (Diğer modüller için varsayılan)
    prompt_general = """
    Sen uzman bir yazılım test mühendisisin. 
    Aşağıda verilen senaryoyu analiz et ve profesyonel bir 'unittest' kodu yaz.
    
    KURALLAR:
    1. Sadece Python kodu ver. Açıklama yapma.
    2. Kod bloklarını ```python etiketi içine al.
    3. Test edilecek fonksiyonları 'app' modülünden import et. (from app import ...)
    4. Fonksiyonları testin içinde tekrar tanımlama, import et.
    """

    # 2. YENİ PROMPT (Modül 1 için Test Case odaklı)
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

    # Mod seçimi
    if mode == "test_case":
        system_instruction = prompt_test_case
    else:
        system_instruction = prompt_general
    
    # Streamlit için özel ekleme (Her iki modda da geçerli olabilir)
    if fix_for_streamlit:
        system_instruction += """
        ÇOK ÖNEMLİ TEKNİK KURAL:
        Kodun en altına MUTLAKA şu bloğu ekle:
        if __name__ == '__main__':
            import unittest
            unittest.main(argv=['first-arg-is-ignored'], exit=False)
        """

    full_prompt = f"{system_instruction}\n\nKullanıcı Girdisi:\n{user_prompt}"

    safety_settings = [
        { "category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE" },
        { "category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE" },
        { "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE" },
        { "category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE" },
    ]

    # --- ROTASYON DÖNGÜSÜ ---
    max_attempts = len(api_keys) * 3 
    
    for attempt in range(max_attempts):
        current_key_index = attempt % len(api_keys)
        current_key = api_keys[current_key_index]
        
        try:
            genai.configure(api_key=current_key)
            model = genai.GenerativeModel('gemini-flash-latest')
            
            response = model.generate_content(full_prompt, safety_settings=safety_settings)
            
            if not response.parts:
                if hasattr(response, 'prompt_feedback'):
                     return f"AI cevap veremedi. Filtre: {response.prompt_feedback}"
                return "AI boş cevap döndürdü."
                
            cleaned_code = response.text.replace("```python", "").replace("```", "").strip()
            return cleaned_code

        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg or "quota" in error_msg.lower():
                print(f"⚠️ Anahtar {current_key_index + 1} kotası doldu! Sıradaki anahtara geçiliyor... (Hata: 429)")
                time.sleep(1)
                continue 
            else:
                return f"Beklenmeyen Hata: {error_msg}"

    return "Hata: Tüm API anahtarlarının kotası dolu! Biraz bekleyin."