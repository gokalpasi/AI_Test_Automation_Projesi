import streamlit as st
import os
from dotenv import load_dotenv
import pandas as pd
import ast  # SÖZDİZİMİ KONTROLÜ İÇİN EKLENDİ

# Modüllerin import edilmesi
from modules.ai_generator import generate_test_code_from_gemini
from modules.metrics import calculate_metrics
from modules.coverage_tool import run_coverage_analysis
from modules.visualizer import create_call_graph
# --- YENİ GÜNCELLENEN AJAN MODÜLÜ ---
from modules.agent import AutoTestAgent 

# .env yükle
load_dotenv()

# --- YARDIMCI FONKSİYON: GÜVENLİK KONTROLÜ ---
def is_valid_python(code):
    """Kodun sözdizimsel olarak doğru olup olmadığını kontrol eder."""
    if not code.strip():
        return False, "Kod alanı boş olamaz."
    try:
        ast.parse(code)
        return True, ""
    except SyntaxError as e:
        return False, f"Yazım Hatası (Satır {e.lineno}): {e.msg}"

st.set_page_config(page_title="AI Test Otomasyonu (RL Destekli)", layout="wide")

st.sidebar.title("Navigasyon")
secim = st.sidebar.radio("Modül Seçin:", [
    "Modül 1: Kod Üretimi & Analiz", 
    "Modül 2: Test Kapsamı (Coverage)", 
    "Modül 3: Otonom Ajan (RL & LLM)"
])

# ==============================================================================
# MODÜL 1: KOD ÜRETİMİ & ANALİZ (AYNEN KORUNDU)
# ==============================================================================
if secim == "Modül 1: Kod Üretimi & Analiz":
    st.header("📝 Modül 1: Test Case'den Kod Üretimi")
    st.info("Aşağıya test senaryolarınızı içeren tabloyu veya metni yapıştırın.")

    user_input = st.text_area(
        "Test Senaryosu / Tablo:",
        height=150,
        placeholder="Örn: Bir hesap makinesi uygulaması için toplama testi..."
    )

    if st.button("Kod Üret ve Analiz Et"):
        if not user_input:
            st.warning("Lütfen önce bir senaryo girin!")
        else:
            with st.spinner("Gemini çalışıyor..."):
                generated_code = generate_test_code_from_gemini(user_input)

                if "AI cevap veremedi" in generated_code or "Hata:" in generated_code:
                    st.error("⚠️ Kod üretilemedi.")
                    st.warning(generated_code)
                else:
                    st.success("✅ Kod başarıyla üretildi!")

                    col1, col2 = st.columns([1, 1])

                    with col1:
                        st.subheader("🐍 Üretilen Python Test Kodu")
                        st.code(generated_code, language='python')

                    with col2:
                        st.subheader("📊 Analiz Raporu")
                        df_metrics, error_metrics = calculate_metrics(generated_code)
                        metrics_list_for_graph = []

                        if error_metrics:
                            st.error(f"Metrik hatası: {error_metrics}")
                            metrics_list_for_graph = ["Metrik Hesaplanamadı"]
                        else:
                            st.table(df_metrics)
                            if not df_metrics.empty:
                                for index, row in df_metrics.iterrows():
                                    metrics_list_for_graph.append(f"{row.iloc[0]}: {row.iloc[1]}")

                    st.markdown("---")
                    st.subheader("🕸️ Fonksiyon Çağrı Akışı (Call Graph)")

                    try:
                        fig = create_call_graph(
                            user_scenario=user_input[:40] + "..." if len(user_input) > 40 else user_input,
                            generated_code=generated_code,
                            metrics=metrics_list_for_graph
                        )
                        st.pyplot(fig)
                    except Exception as e:
                        st.error(f"Grafik oluşturulurken bir hata oluştu: {e}")

# ==============================================================================
# MODÜL 2: COVERAGE (AYNEN KORUNDU)
# ==============================================================================
elif secim == "Modül 2: Test Kapsamı (Coverage)":
    st.header("📊 Modül 2: Test Coverage Analizi")
    st.markdown("Test kodunuzun, kaynak kodun ne kadarını kapsadığını ölçün.")

    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("1. Kaynak Kod (Source Code)")
        src_file = st.file_uploader("📂 Bir .py dosyası yükleyin (Kaynak Kod)", type=["py"], key="src_uploader")
        default_src = """class GradeCalculator:\n    def calculate_status(self, score):\n        if score < 0 or score > 100: return "Geçersiz Not"\n        elif score >= 50: return "Geçti"\n        else: return "Kaldı" """
        
        if src_file is not None:
            source_code_input = src_file.read().decode("utf-8")
            st.success(f"📄 Dosya yüklendi: {src_file.name}")
            with st.expander("Dosya İçeriğini Gör"):
                st.code(source_code_input, language='python')
        else:
            source_code_input = st.text_area("Veya kodu buraya yapıştırın:", value=default_src, height=250, key="src_code")

    with col2:
        st.subheader("2. Test Kodu (Test Script)")
        test_file = st.file_uploader("📂 Bir .py dosyası yükleyin (Test Kodu)", type=["py"], key="test_uploader")
        default_test = """import unittest\nclass TestGradeCalculator(unittest.TestCase):\n    def setUp(self): self.calc = GradeCalculator()\n    def test_pass_situation(self):\n        sonuc = self.calc.calculate_status(75)\n        self.assertEqual(sonuc, "Geçti")"""
        
        if test_file is not None:
            test_code_input = test_file.read().decode("utf-8")
            st.success(f"📄 Dosya yüklendi: {test_file.name}")
            with st.expander("Dosya İçeriğini Gör"):
                st.code(test_code_input, language='python')
        else:
            test_code_input = st.text_area("Veya kodu buraya yapıştırın:", value=default_test, height=250, key="test_code")

    if st.button("Coverage Analizini Başlat", type="primary"):
        valid_src, msg_src = is_valid_python(source_code_input)
        valid_test, msg_test = is_valid_python(test_code_input)

        if not valid_src:
            st.error(f"❌ Kaynak Kod Hatalı: {msg_src}")
        elif not valid_test:
            st.error(f"❌ Test Kodu Hatalı: {msg_test}")
        else:
            with st.spinner("Coverage hesaplanıyor..."):
                result, error = run_coverage_analysis(source_code_input, test_code_input)

                if error:
                    st.error(f"⚠️ Analiz sırasında mantıksal bir hata oluştu: {error}")
                else:
                    st.success("✅ Analiz Tamamlandı!")
                    m1, m2, m3 = st.columns(3)
                    cov_percent = int(result['coverage_percent'])
                    m1.metric("Kapsama Oranı (Coverage)", f"%{cov_percent}", delta_color="normal" if cov_percent > 80 else "inverse")
                    m2.metric("Durum", "Başarılı" if result['success'] else "Hatalı")
                    m3.metric("Test Edilmeyen Satır Sayısı", len(result['missed_lines']))
                    st.progress(cov_percent)
                    st.markdown("---")
                    st.subheader("🔍 Detaylı Satır Analizi")

                    if result['missed_lines']:
                        st.warning(f"⚠️ Dikkat: Kodunuzun {len(result['missed_lines'])} satırı test edilmedi.")
                        with st.expander("Test Edilmeyen Satırları Kod Üzerinde Gör", expanded=True):
                            src_lines = source_code_input.split('\n')
                            annotated_code = []
                            for i, line in enumerate(src_lines, 1):
                                if i in result['missed_lines']:
                                    annotated_code.append(f"{line:<50}  # <--- 🔴 TEST EDİLMEDİ (Satır {i})")
                                else:
                                    annotated_code.append(f"{line:<50}  # 🟢 OK")
                            st.code("\n".join(annotated_code), language="python")
                    else:
                        st.balloons()
                        st.success("Tebrikler! %100 Kapsama oranına ulaştınız.")

# ==============================================================================
# MODÜL 3: OTONOM AJAN (RL + LLM HİBRİT YAPISI) - GÜNCELLENDİ
# ==============================================================================
elif secim == "Modül 3: Otonom Ajan (RL & LLM)":
    st.header("🧠 Modül 3: RL Destekli Otonom Ajan")
    st.markdown("""
    Bu modül, **Reinforcement Learning (Q-Learning)** kullanarak en iyi prompt stratejisini öğrenir 
    ve **LLM (Gemini)** kullanarak test kodu yazar.
    """)

    # Kaynak Kod Girişi
    source_code = st.text_area(
        "Test Edilecek Kaynak Kod:", 
        height=200, 
        placeholder="Python fonksiyonunuzu buraya yapıştırın..."
    )

    if st.button("Ajanı Başlat 🚀"):
        if not source_code.strip():
            st.error("Lütfen kaynak kod girin.")
        else:
            # Ajanı başlat
            agent = AutoTestAgent(source_code, max_retries=5)
            
            status_container = st.container()
            
            with st.spinner("RL Ajanı devrede... Stratejiler (Actions) deneniyor..."):
                final_result, history = agent.run()
            
            st.success("İşlem Tamamlandı!")
            
            # --- 1. Q-TABLE GÖRSELLEŞTİRME (RL KANITI) ---
            st.subheader("🧠 Q-Learning Hafızası (Q-Table)")
            st.info("Ajanın deneyimlerine göre hangi durumda hangi stratejiye (Action) kaç puan verdiğini gösterir.")
            
            # YARDIM BUTONU (EXPANDER)
            with st.expander("❓ Bu Tablo Nasıl Okunur? (Tıkla ve Öğren)"):
                st.markdown("""
                Bu tablo, Yapay Zeka ajanının **"Beynini"** temsil eder.
                
                * **Satırlar (Sol Taraf):** Ajanın o an içinde bulunduğu durum (Örn: `BASLANGIC`, `TEST_BASARISIZ`).
                * **Sütunlar (Üst Taraf):** Ajanın seçebileceği stratejiler (Actions).
                * **Renkler:**
                    * 🟢 **YEŞİL (Pozitif Puan):** Ajan bu hamleyi yaptığında ödül almıştır (Coverage artmıştır). Bu stratejiyi sevmeye başlar.
                    * 🔴 **KIRMIZI (Negatif Puan):** Ajan bu hamleyi yaptığında hata almıştır (Syntax Error vb.). Bu stratejiden kaçınır.
                    * ⚪ **BEYAZ (0.00):** Henüz bu durumda bu stratejiyi denememiştir.
                """)

            # Agent'ın beynindeki tabloyu al
            q_data = agent.brain.q_table
            
            if q_data:
                # Pandas DataFrame oluştur
                df_q = pd.DataFrame.from_dict(q_data, orient='index')

                # RENKLENDİRME FONKSİYONU
                def renklendir(val):
                    color = ''
                    if val > 0:
                        color = 'background-color: #d4edda; color: black' # Açık Yeşil
                    elif val < 0:
                        color = 'background-color: #f8d7da; color: black' # Açık Kırmızı
                    return color

                # Tabloyu renklendir ve formatla
                st.dataframe(df_q.style.applymap(renklendir).format("{:.2f}"))
            else:
                st.write("Henüz öğrenilmiş veri yok.")

            # --- 2. ADIM ADIM GEÇMİŞ ---
            st.subheader("🕵️‍♂️ Ajanın Karar Süreci")
            
            for step in history:
                durum_ikonu = "✅" if step['status'] == "Mükemmel" else "⚠️" if step['status'] == "İyileştirilmeli" else "❌"
                
                # Başlıkta Ajanın seçtiği ACTION'ı gösteriyoruz
                with st.expander(f"Adım {step['attempt']} - Seçilen Strateji: {step['action']} -> Sonuç: {durum_ikonu} {step['status']}"):
                    st.write(f"**Detay:** {step['details']}")
                    st.markdown("**Üretilen Kod:**")
                    st.code(step['code'], language='python')
            
            # --- 3. NİHAİ SONUÇ ---
            st.markdown("---")
            st.subheader("🏆 Nihai (En İyi) Sonuç")
            
            if final_result['status'] == "Hata":
                st.error("Ajan maksimum deneme sayısına ulaştı ancak tamamen hatasız bir test üretemedi.")
                st.error(f"Son Hata Mesajı: {final_result['details']}")
            else:
                st.balloons()
                st.success(f"Başarılı! Coverage: {final_result['details']}")
                st.code(final_result['code'], language='python')