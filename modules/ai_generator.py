import google.generativeai as genai
import os

def generate_test_code_from_gemini(user_prompt):
    """
    Kullanıcıdan gelen test senaryosu metnini alır,
    Gemini API'ye gönderir ve üretilen Python test kodunu döndürür.
    """
    
    # API Anahtarını al
    api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        return "Hata: API Key bulunamadı."

    try:
        # Gemini Ayarları
        genai.configure(api_key=api_key)
        # Senin için çalışan model buydu, bunu değiştirmeyelim:
        model = genai.GenerativeModel('gemini-flash-latest') 

        # Gemini'ye gönderilecek asıl komut
        system_instruction = """
        Sen uzman bir yazılım test mühendisisin. 
        Aşağıda verilen test senaryosu tablosunu veya açıklamasını analiz et.
        Buna uygun, profesyonel, 'unittest' kütüphanesini kullanan bir Python test kodu yaz.
        Sadece Python kodunu ver, açıklama metni yazma. 
        Kod bloklarını ```python etiketi içine al.
        """
        
        full_prompt = f"{system_instruction}\n\nKullanıcı Girdisi:\n{user_prompt}"

        # --- GÜVENLİK AYARLARI (YENİ KISIM) ---
        # AI'ın kod yazarken gereksiz yere bloklanmasını engellemek için filtreleri kapatıyoruz.
        safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
        ]

        # Cevabı al (Güvenlik ayarlarıyla birlikte)
        response = model.generate_content(full_prompt, safety_settings=safety_settings)
        
        # --- HATA KONTROLÜ (YENİ KISIM) ---
        # Cevap boş mu dolu mu kontrol edelim (Senin aldığın hatayı burası çözecek)
        if not response.parts:
            # Eğer cevap boşsa ama bir sebep varsa onu yazdıralım
            if hasattr(response, 'prompt_feedback'):
                return f"AI cevap veremedi. Filtre sebebi olabilir: {response.prompt_feedback}"
            return "AI boş bir cevap döndürdü. Lütfen tekrar deneyin."
            
        # Gelen metinden kodu ayıkla
        cleaned_code = response.text.replace("```python", "").replace("```", "").strip()
        
        return cleaned_code

    except Exception as e:
        return f"Bir hata oluştu: {str(e)}"