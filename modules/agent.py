import time
from modules.ai_generator import generate_test_code_from_gemini
from modules.coverage_tool import run_coverage_analysis
from modules.rl_brain import QLearningBrain


class AutoTestAgent:
    """
    Takviyeli Öğrenme (RL) kullanarak bir kaynak kod için otomatik birim testler
    üreten ve coverage (kapsam) oranını maksimize etmeye çalışan otonom ajan.
    """

    def __init__(self, source_code, max_retries=5):
        self.source_code = source_code
        self.max_retries = max_retries
        self.history = []

        # --- Takviyeli Öğrenme (RL) Konfigürasyonu ---
        # Ajanın seçebileceği stratejik eylem uzayı (Action Space)
        self.actions = ["STRATEJI_STANDART", "STRATEJI_SADELESTIR", "STRATEJI_GENISLET", "STRATEJI_EDGE_CASE"]
        # Q-Learning beyni: Eylemlerin değerlerini (Q-values) saklayan ve güncelleyen motor
        self.brain = QLearningBrain(actions=self.actions)

    def _get_prompt_by_action(self, action, error_msg="", coverage_info=""):
        """
        Seçilen aksiyona göre LLM'e (Gemini) gönderilecek özelleştirilmiş
        komut setini (prompt) hazırlar.
        """
        base_instruction = """
        Aşağıdaki Python kodu için 'unittest' kütüphanesini kullanarak test dosyası yaz.
        KURALLAR:
        1. Hedef fonksiyonu/sınıfı ASLA TEKRAR TANIMLAMA. Sadece import et: 'from app import *'
        2. Sadece Python kodunu ver.
        """

        if action == "STRATEJI_STANDART":
            return f"{base_instruction}\nGenel ve kapsamlı testler yaz.\nKod:\n{self.source_code}"

        elif action == "STRATEJI_SADELESTIR":
            # Syntax hatalarında veya karmaşık import problemlerinde ajanı temel yapıya döndürür
            return f"{base_instruction}\nÖnceki kod HATA verdi: {error_msg}\nLütfen kodu SADELEŞTİR. Karmaşık yapılardan kaçın, sadece temel importları yap.\nKod:\n{self.source_code}"

        elif action == "STRATEJI_GENISLET":
            # Düşük coverage durumunda spesifik olarak çalıştırılmamış satırlara odaklanır
            return f"{base_instruction}\nCoverage Düşük kaldı. Şu satırlar test edilmedi: {coverage_info}\nLütfen sadece bu eksik satırları hedefleyen testler ekle.\nKod:\n{self.source_code}"

        elif action == "STRATEJI_EDGE_CASE":
            # Yüksek coverage sağlandığında %100'e ulaşmak için uç durumları zorlar
            return f"{base_instruction}\nTestler çalışıyor ama coverage %100 değil. Lütfen 'Edge Case' (Sınır durumları: None, 0, negatif, boş liste) testleri ekle.\nKod:\n{self.source_code}"

        return f"{base_instruction}\nKod:\n{self.source_code}"

    def _determine_state(self, result, error_msg, current_coverage):
        """
        Gözlem Alanı (State Determination): Mevcut test sonuçlarını ve
        coverage verilerini analiz ederek ajanın içinde bulunduğu durumu tanımlar.
        """
        # Hatalı durumların tespiti (Ajanın negatif feedback alacağı durumlar)
        if error_msg:
            return "DURUM_SYNTAX_HATA"

        if not result['success']:
            # Kod geçerli ama mantıksal (assertion) hatalar mevcut
            return "DURUM_TEST_BASARISIZ"

        # Başarı seviyelerinin gruplandırılması (Binning)
        # Sürekli veriyi (0-100) ayrık durumlara çevirerek Q-Table karmaşıklığını azaltır
        cov = result['coverage_percent']

        if cov == 100:
            return "DURUM_MUKEMMEL"
        elif cov < 20:
            return "DURUM_COV_COK_DUSUK"
        elif cov < 50:
            return "DURUM_COV_DUSUK"
        elif cov < 80:
            return "DURUM_COV_ORTA"
        else:
            return "DURUM_COV_YUKSEK"

    def run(self):
        """
        Ana döngü: Karar alma (Action), Uygulama (Execution), Gözlem (State)
        ve Öğrenme (Reward) adımlarını içeren iterasyon süreci.
        """
        current_coverage = 0
        state = "DURUM_BASLANGIC"

        for attempt in range(1, self.max_retries + 1):
            step_info = {"attempt": attempt, "status": "", "details": "", "action": ""}

            # 1. ADIM: EYLEM SEÇİMİ (Exploration vs Exploitation)
            action = self.brain.choose_action(state)
            step_info["action"] = action

            # Context hazırlığı: Önceki denemelerden gelen hatalar ve eksik satırlar
            last_error = self.history[-1]['details'] if self.history and self.history[-1]['status'] == "Hata" else ""
            last_missed = str(self.history[-1]['missed_lines']) if self.history and 'missed_lines' in self.history[
                -1] else ""

            # 2. ADIM: KOD ÜRETİMİ (LLM Entegrasyonu)
            prompt = self._get_prompt_by_action(action, last_error, last_missed)
            generated_code = generate_test_code_from_gemini(prompt)
            step_info["code"] = generated_code

            # 3. ADIM: ANALİZ (Testlerin Çalıştırılması ve Kapsam Ölçümü)
            result, error_msg = run_coverage_analysis(self.source_code, generated_code)

            # 4. ADIM: DURUM GEÇİŞİ VE ÖDÜL MEKANİZMASI (Reward Shaping)
            next_state = self._determine_state(result, error_msg, current_coverage)

            reward = 0
            new_coverage = result.get('coverage_percent', 0) if result else 0

            # --- Ödül Fonksiyonu Tasarımı ---
            if next_state == "DURUM_SYNTAX_HATA":
                reward = -20  # Negatif Reward: Kodun çalışmaması en büyük engeldir
                step_info.update({"status": "Hata", "details": error_msg})

            elif next_state == "DURUM_TEST_BASARISIZ":
                reward = -10  # Negatif Reward: Mantıksal tutarsızlık cezası
                step_info.update({"status": "Test Başarısız", "details": "Assertion Error"})

            elif next_state == "DURUM_MUKEMMEL":
                # Pozitif Reward: %100 başarı ve zaman verimliliği teşviki
                reward = 100 + (10 / attempt)
                step_info.update({"status": "Mükemmel", "details": "Coverage: %100"})

            else:
                # Dinamik Kapsam Analizi: İlerleme varsa ödüllendir, gerileme varsa cezalandır
                diff = new_coverage - current_coverage

                if diff > 0:
                    reward = diff * 2  # Pozitif Reward: Kapsam artışı teşvik edilir
                    step_info["status"] = "Gelişme"
                elif diff < 0:
                    reward = -50  # Negatif Reward: Regresyon (gerileme) önlenmeye çalışılır
                    step_info["status"] = "Gerileme"
                else:
                    reward = -2  # Küçük Negatif Reward: Zaman kaybını önlemek için durgunluk cezası
                    step_info["status"] = "Sabit"

                step_info["details"] = f"Coverage: %{new_coverage} (Değişim: {diff})"
                current_coverage = new_coverage
                if result: step_info["missed_lines"] = result.get('missed_lines', [])

            # 5. ADIM: ÖĞRENME (Bellman Denklemine Dayalı Q-Table Güncellemesi)
            self.brain.learn(state, action, reward, next_state)

            # Döngü sonu hazırlıkları ve başarı kontrolü
            state = next_state
            self.history.append(step_info)

            if next_state == "DURUM_MUKEMMEL":
                return step_info, self.history

            # API hız limitlerini (Rate Limit) aşmamak için kısa bekleme
            time.sleep(1)

        return self.history[-1], self.history