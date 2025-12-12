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

st.set_page_config(page_title="AI Test Otomasyonu", layout="wide")

st.sidebar.title("Navigasyon")
secim = st.sidebar.radio("Modül Seçin:", ["Modül 1: Kod Üretimi & Analiz", "Modül 2: Test Kapsamı (Coverage)"])

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

                # --- HATA KONTROLÜ ---
                if "AI cevap veremedi" in generated_code or "Hata:" in generated_code or "Bir hata oluştu" in generated_code:
                    st.error("⚠️ Kod üretilemedi. AI şu yanıtı verdi:")
                    st.warning(generated_code)
                else:
                    st.success("✅ Kod başarıyla üretildi!")

                    # Sayfayı ikiye bölüyoruz (Kod ve Metrik Tablosu)
                    col1, col2 = st.columns([1, 1])

                    with col1:
                        st.subheader("🐍 Üretilen Python Test Kodu")
                        st.code(generated_code, language='python')

                    with col2:
                        st.subheader("📊 Analiz Raporu")

                        # Metrikleri hesapla
                        df_metrics, error_metrics = calculate_metrics(generated_code)

                        # Grafik için metrik listesi hazırlığı
                        metrics_list_for_graph = []

                        if error_metrics:
                            st.error(f"Metrik hatası: {error_metrics}")
                            metrics_list_for_graph = ["Metrik Hesaplanamadı"]
                        else:
                            st.table(df_metrics)
                            if not df_metrics.empty:
                                for index, row in df_metrics.iterrows():
                                    metrics_list_for_graph.append(f"{row.iloc[0]}: {row.iloc[1]}")

                    # --- CALL GRAPH ---
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
# MODÜL 2: COVERAGE (GELİŞTİRİLMİŞ VERSİYON: DOSYA YÜKLEME + SYNTAX KONTROLÜ)
# ==============================================================================
elif secim == "Modül 2: Test Kapsamı (Coverage)":
    st.header("📊 Modül 2: Test Coverage Analizi")
    st.markdown("Test kodunuzun, kaynak kodun ne kadarını kapsadığını ölçün.")

    col1, col2 = st.columns(2)
    
    # --- KOLON 1: KAYNAK KOD ---
    with col1:
        st.subheader("1. Kaynak Kod (Source Code)")
        # Dosya Yükleyici
        src_file = st.file_uploader("📂 Bir .py dosyası yükleyin (Kaynak Kod)", type=["py"], key="src_uploader")
        
        default_src = """class GradeCalculator:\n    def calculate_status(self, score):\n        if score < 0 or score > 100: return "Geçersiz Not"\n        elif score >= 50: return "Geçti"\n        else: return "Kaldı" """
        
        # Eğer dosya yüklendiyse içeriğini oku, yüklenmediyse text area'yı kullan
        if src_file is not None:
            source_code_input = src_file.read().decode("utf-8")
            st.success(f"📄 Dosya yüklendi: {src_file.name}")
            with st.expander("Dosya İçeriğini Gör"):
                st.code(source_code_input, language='python')
        else:
            source_code_input = st.text_area("Veya kodu buraya yapıştırın:", value=default_src, height=250, key="src_code")

    # --- KOLON 2: TEST KODU ---
    with col2:
        st.subheader("2. Test Kodu (Test Script)")
        # Dosya Yükleyici
        test_file = st.file_uploader("📂 Bir .py dosyası yükleyin (Test Kodu)", type=["py"], key="test_uploader")
        
        default_test = """import unittest\nclass TestGradeCalculator(unittest.TestCase):\n    def setUp(self): self.calc = GradeCalculator()\n    def test_pass_situation(self):\n        sonuc = self.calc.calculate_status(75)\n        self.assertEqual(sonuc, "Geçti")"""
        
        # Eğer dosya yüklendiyse içeriğini oku
        if test_file is not None:
            test_code_input = test_file.read().decode("utf-8")
            st.success(f"📄 Dosya yüklendi: {test_file.name}")
            with st.expander("Dosya İçeriğini Gör"):
                st.code(test_code_input, language='python')
        else:
            test_code_input = st.text_area("Veya kodu buraya yapıştırın:", value=default_test, height=250, key="test_code")

    # --- ANALİZ BUTONU ---
    if st.button("Coverage Analizini Başlat", type="primary"):
        # 1. ADIM: SÖZDİZİMİ (SYNTAX) KONTROLÜ
        valid_src, msg_src = is_valid_python(source_code_input)
        valid_test, msg_test = is_valid_python(test_code_input)

        if not valid_src:
            st.error(f"❌ Kaynak Kod Hatalı: {msg_src}")
        elif not valid_test:
            st.error(f"❌ Test Kodu Hatalı: {msg_test}")
        
        # 2. ADIM: ANALİZİ ÇALIŞTIR (Eğer kodlar sağlamsa)
        else:
            with st.spinner("Coverage hesaplanıyor..."):
                result, error = run_coverage_analysis(source_code_input, test_code_input)

                if error:
                    st.error(f"⚠️ Analiz sırasında mantıksal bir hata oluştu: {error}")
                else:
                    st.success("✅ Analiz Tamamlandı!")

                    # --- ÖZET METRİKLER ---
                    m1, m2, m3 = st.columns(3)

                    cov_percent = int(result['coverage_percent'])

                    m1.metric("Kapsama Oranı (Coverage)", f"%{cov_percent}", delta_color="normal" if cov_percent > 80 else "inverse")
                    m2.metric("Durum", "Başarılı" if result['success'] else "Hatalı")
                    m3.metric("Test Edilmeyen Satır Sayısı", len(result['missed_lines']))

                    # Progress Bar
                    st.progress(cov_percent)
                    st.markdown("---")

                    # --- DETAYLI SATIR ANALİZİ ---
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
                        st.success("Tebrikler! %100 Kapsama oranına ulaştınız. Tüm satırlar test ediliyor.")