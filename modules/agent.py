import time
from modules.ai_generator import generate_test_code_from_gemini
from modules.coverage_tool import run_coverage_analysis
from modules.rl_brain import QLearningBrain

class AutoTestAgent:
    def __init__(self, source_code, max_retries=5):
        self.source_code = source_code
        self.max_retries = max_retries
        self.history = [] 
        
        # --- RL AYARLARI ---
        self.actions = ["STRATEJI_STANDART", "STRATEJI_SADELESTIR", "STRATEJI_GENISLET", "STRATEJI_EDGE_CASE"]
        self.brain = QLearningBrain(actions=self.actions)

    def _get_prompt_by_action(self, action, error_msg="", coverage_info=""):
        """Prompt stratejileri aynen kalıyor."""
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
             return f"{base_instruction}\nTestler çalışıyor ama coverage %100 değil. Lütfen 'Edge Case' (Sınır durumları: None, 0, negatif, boş liste) testleri ekle.\nKod:\n{self.source_code}"
        
        return f"{base_instruction}\nKod:\n{self.source_code}"

    def _determine_state(self, result, error_msg, current_coverage):
        """
        GELİŞTİRİLMİŞ STATE (DURUM) BELİRLEME
        Artık coverage oranına göre farklı durumlar döndürüyoruz.
        """
        # 1. Hata Durumları
        if error_msg:
            # Syntax hatası mı yoksa import hatası mı? Genel olarak HATA diyelim.
            return "DURUM_SYNTAX_HATA"
        
        if not result['success']:
            # Kod çalıştı ama assertion hatası var (Test geçmedi)
            return "DURUM_TEST_BASARISIZ"

        # 2. Başarı ve Coverage Durumları (Binning)
        cov = result['coverage_percent']
        
        if cov == 100:
            return "DURUM_MUKEMMEL"
        elif cov < 20:
            return "DURUM_COV_COK_DUSUK"  # %0-20
        elif cov < 50:
            return "DURUM_COV_DUSUK"      # %20-50
        elif cov < 80:
            return "DURUM_COV_ORTA"       # %50-80
        else:
            return "DURUM_COV_YUKSEK"     # %80-99 (Artık Edge case lazım)

    def run(self):
        # İlk başta durum coverage 0 olduğu için çok düşük başlar
        current_coverage = 0
        state = "DURUM_BASLANGIC" 
        
        last_generated_code = "" # Önceki kodu saklayalım (Regresyon kontrolü için opsiyonel)

        for attempt in range(1, self.max_retries + 1):
            step_info = {"attempt": attempt, "status": "", "details": "", "action": ""}
            
            # 1. EYLEM SEÇ
            action = self.brain.choose_action(state)
            step_info["action"] = action
            
            # Context verilerini hazırla
            last_error = self.history[-1]['details'] if self.history and self.history[-1]['status'] == "Hata" else ""
            
            # Eksik satırları string'e çevir
            last_missed = ""
            if self.history and 'missed_lines' in self.history[-1]:
                 last_missed = str(self.history[-1]['missed_lines'])

            # 2. KOD ÜRET
            prompt = self._get_prompt_by_action(action, last_error, last_missed)
            generated_code = generate_test_code_from_gemini(prompt)
            step_info["code"] = generated_code
            
            # 3. ÇALIŞTIR VE ÖLÇ
            result, error_msg = run_coverage_analysis(self.source_code, generated_code)
            
            # 4. YENİ DURUMU VE ÖDÜLÜ BELİRLE (REWARD SHAPING)
            next_state = self._determine_state(result, error_msg, current_coverage)
            
            reward = 0
            new_coverage = 0
            
            if result and 'coverage_percent' in result:
                new_coverage = result['coverage_percent']
            
            # --- GELİŞMİŞ ÖDÜL SİSTEMİ ---
            
            if next_state == "DURUM_SYNTAX_HATA":
                reward = -20  # Kod çalışmıyor bile, büyük ceza.
                step_info["status"] = "Hata"
                step_info["details"] = error_msg
                
            elif next_state == "DURUM_TEST_BASARISIZ":
                reward = -10  # Mantık hatası
                step_info["status"] = "Test Başarısız"
                step_info["details"] = "Assertion Error"
                
            elif next_state == "DURUM_MUKEMMEL":
                reward = 100 + (10 / attempt) # Mükemmel + Hız bonusu (erken çözerse daha çok puan)
                step_info["status"] = "Mükemmel"
                step_info["details"] = "Coverage: %100"
                
            else:
                # Coverage analizi (İlerleme mi var, gerileme mi?)
                diff = new_coverage - current_coverage
                
                if diff > 0:
                    # İlerleme var! Aradaki fark kadar puan ver.
                    # Hatta teşvik etmek için farkı 2 ile çarpabiliriz.
                    reward = diff * 2 
                    step_info["status"] = "Gelişme"
                elif diff < 0:
                    # GERİLEME! Önceki kod daha iyiydi. Bunu yapma.
                    reward = -50 
                    step_info["status"] = "Gerileme"
                else:
                    # Yerinde sayma. Aynı coverage'da kaldı.
                    # Zaman harcadığı için ufak bir ceza.
                    reward = -2 
                    step_info["status"] = "Sabit"
                
                step_info["details"] = f"Coverage: %{new_coverage} (Değişim: {diff})"
                current_coverage = new_coverage # Coverage'ı güncelle
                if result: step_info["missed_lines"] = result.get('missed_lines', [])

            # 5. ÖĞREN (Q-TABLE GÜNCELLEME)
            self.brain.learn(state, action, reward, next_state)
            
            # State güncelle
            state = next_state
            self.history.append(step_info)
            
            if next_state == "DURUM_MUKEMMEL":
                return step_info, self.history
            
            # Çok hızlı API isteği atmamak için bekleme
            time.sleep(1)

        return self.history[-1], self.history