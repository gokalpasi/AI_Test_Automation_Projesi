import time
from modules.ai_generator import generate_test_code_from_gemini
from modules.coverage_tool import run_coverage_analysis
from modules.rl_brain import QLearningBrain  # YENİ BEYİN

class AutoTestAgent:
    def __init__(self, source_code, max_retries=5):
        self.source_code = source_code
        self.max_retries = max_retries
        self.history = [] 
        
        # --- RL AYARLARI ---
        # Aksiyonlarımız (Farklı Prompt Stratejileri)
        self.actions = ["STRATEJI_STANDART", "STRATEJI_SADELESTIR", "STRATEJI_GENISLET", "STRATEJI_EDGE_CASE"]
        self.brain = QLearningBrain(actions=self.actions)

    def _get_prompt_by_action(self, action, error_msg="", coverage_info=""):
        """RL'in seçtiği aksiyona göre prompt üretir."""
        
        base_instruction = """
        Aşağıdaki Python kodu için 'unittest' kütüphanesini kullanarak test dosyası yaz.
        KURALLAR:
        1. Hedef fonksiyonu/sınıfı ASLA TEKRAR TANIMLAMA. Sadece import et: 'from app import *'
        2. Sadece Python kodunu ver.
        """
        
        if action == "STRATEJI_STANDART":
            return f"{base_instruction}\nGenel ve kapsamlı testler yaz.\nKod:\n{self.source_code}"
        
        elif action == "STRATEJI_SADELESTIR":
            return f"{base_instruction}\nÖnceki kod HATA verdi: {error_msg}\nLütfen kodu SADELEŞTİR. Karmaşık yapılardan kaçın, sadece temel importları yap.\nKod:\n{self.source_code}"
            
        elif action == "STRATEJI_GENISLET":
             return f"{base_instruction}\nCoverage Düşük kaldı. Şu satırlar test edilmedi: {coverage_info}\nLütfen sadece bu eksik satırları hedefleyen testler ekle.\nKod:\n{self.source_code}"
             
        elif action == "STRATEJI_EDGE_CASE":
             return f"{base_instruction}\nBazı mantık hataları var. Lütfen 'Edge Case' (Sınır durumları) için, örneğin None, 0, negatif değerler, boş liste gibi durumları test et.\nKod:\n{self.source_code}"
        
        return f"{base_instruction}\nKod:\n{self.source_code}"

    def _determine_state(self, result, error_msg):
        """Mevcut durumu (State) analiz eder."""
        if error_msg:
            return "HATA_ALINDI"
        elif result and result['success'] and result['coverage_percent'] == 100:
            return "MUKEMMEL"
        elif result and result['success']:
            return "DUSUK_COVERAGE"
        else:
            return "TEST_BASARISIZ"

    def run(self):
        # Başlangıç Durumu
        state = "BASLANGIC"
        current_coverage = 0
        
        for attempt in range(1, self.max_retries + 1):
            step_info = {"attempt": attempt, "status": "", "details": "", "action": ""}
            
            # 1. RL BEYNİ KARAR VERİYOR
            action = self.brain.choose_action(state)
            step_info["action"] = action # Ekrana yazdırmak için
            
            # 2. SEÇİLEN STRATEJİYE GÖRE KOD ÜRETİLİYOR (LLM)
            # Hata mesajı veya coverage bilgisini önceki adımdan almamız lazım ama 
            # ilk adımda boş olacak.
            last_error = self.history[-1]['details'] if self.history and self.history[-1]['status'] == "Hata" else ""
            last_missed = "" # Basitleştirildi
            
            prompt = self._get_prompt_by_action(action, last_error, last_missed)
            generated_code = generate_test_code_from_gemini(prompt)
            
            # 3. ORTAMDA ÇALIŞTIR (Environment Step)
            result, error_msg = run_coverage_analysis(self.source_code, generated_code)
            
            step_info["code"] = generated_code
            
            # 4. YENİ DURUMU BELİRLE VE ÖDÜL VER
            next_state = self._determine_state(result, error_msg)
            reward = 0
            
            if next_state == "HATA_ALINDI":
                reward = -10 # Büyük Ceza
                step_info["status"] = "Hata"
                step_info["details"] = error_msg
                
            elif next_state == "TEST_BASARISIZ":
                reward = -5 # Küçük Ceza (Kod çalıştı ama test geçmedi)
                step_info["status"] = "Test Başarısız"
                step_info["details"] = "Assertion Error"
                
            elif next_state == "DUSUK_COVERAGE":
                # Ödül = Kapsama artışı kadar
                new_cov = result['coverage_percent']
                reward = (new_cov - current_coverage) 
                current_coverage = new_cov
                step_info["status"] = "İyileştirilmeli"
                step_info["details"] = f"Coverage: %{new_cov}"
                
            elif next_state == "MUKEMMEL":
                reward = 100 # Büyük Ödül
                step_info["status"] = "Mükemmel"
                step_info["details"] = "Coverage: %100"
            
            # 5. BEYNİ EĞİT (Q-TABLE UPDATE)
            # Ajan yaptığı eylemin sonucunu öğreniyor
            self.brain.learn(state, action, reward, next_state)
            
            # Durumu güncelle
            state = next_state
            self.history.append(step_info)
            
            if next_state == "MUKEMMEL":
                return step_info, self.history
                
            time.sleep(1)

        return self.history[-1], self.history