"""
Test Coverage Analiz Modülü
Bu modül, test kodlarının kaynak kodu ne kadar kapsadığını (coverage)
ölçmek için Python'un coverage.py aracını kullanır.

Coverage analizi, hangi satırların test edildiğini ve hangilerinin
test edilmediğini gösterir.
"""

import subprocess
import os
import json
import sys
import shutil

def run_coverage_analysis(source_code, test_code):
    """
    Test kodunun kaynak kodu ne kadar kapsadığını (coverage) ölçer.
    
    Bu fonksiyon şu adımları takip eder:
    1. Geçici dosyalar klasörünü temizler ve oluşturur
    2. Kaynak kodu app.py, test kodunu test_app.py olarak kaydeder
    3. Coverage.py aracı ile testleri çalıştırır
    4. Coverage raporunu JSON formatında oluşturur
    5. Raporu analiz ederek coverage yüzdesini ve test edilmeyen satırları bulur
    
    Args:
        source_code (str): Test edilecek kaynak kod
        test_code (str): Test kodu (unittest formatında)
        
    Returns:
        tuple: (sonuç_sözlüğü, hata_mesajı)
            - sonuç_sözlüğü: coverage_percent, missed_lines, success gibi bilgiler içerir
            - hata_mesajı: Hata varsa mesaj, yoksa None
    """
    # --- 1. KLASÖR TEMİZLİĞİ VE HAZIRLIĞI ---
    # Eski geçici dosyaları temizle (önceki analizlerden kalan)
    if os.path.exists("temp_files"):
        try:
            shutil.rmtree("temp_files")  # Klasörü içindekilerle birlikte sil
        except Exception:
            pass  # Silinemezse (dosya açıksa) devam et, hata verme
            
    # Geçici dosyalar klasörünü oluştur
    if not os.path.exists("temp_files"):
        os.makedirs("temp_files")

    # Mutlak yol al (platform bağımsız çalışma için)
    base_dir = os.path.abspath("temp_files")
    
    # Standart isimlendirme: Python modül sistemi ile uyumlu
    source_filename = "app.py"
    test_filename = "test_app.py"
    
    # Dosya yollarını oluştur
    source_path = os.path.join(base_dir, source_filename)
    test_path = os.path.join(base_dir, test_filename)
    json_path = os.path.join(base_dir, "coverage.json")
    
    try:
        # --- 2. DOSYALARI YAZMA ---
        # Kaynak kodu app.py olarak kaydet
        with open(source_path, "w", encoding="utf-8") as f:
            f.write(source_code)
            
        # Test kodunu hazırla ve kaydet
        # Import işlemini garanti altına al: 'from app import *'
        # Bu satır, test dosyasının app.py modülünü görmesini sağlar
        import_line = "from app import *"
        
        # Eğer test kodunda zaten import yoksa, başına ekle
        if "from app import" not in test_code and "import app" not in test_code:
            final_test_code = f"{import_line}\n{test_code}"
        else:
            final_test_code = test_code

        # Test kodunu test_app.py olarak kaydet
        with open(test_path, "w", encoding="utf-8") as f:
            f.write(final_test_code)

        # --- 3. COVERAGE KOMUTU HAZIRLIĞI ---
        # Yöntem: 'python -m coverage run -m unittest test_app'
        # Dosya yolu yerine modül ismi kullanmak (test_app) import hatalarını engeller.
        # --source=app: Sadece app.py dosyasının coverage'ını ölç (test kodunu değil)
        run_command = [
            sys.executable, "-m", "coverage", "run",
            "--source=app",  # Sadece app.py dosyasını takip et
            "-m", "unittest",
            "test_app"       # test_app.py modülünü çalıştır
        ]
        
        # --- 4. TESTLERİ ÇALIŞTIR ---
        # cwd=base_dir: İşlemi temp_files klasörünün içinde yap
        # Bu sayede Python modül sistemi app.py ve test_app.py'yi bulabilir
        process = subprocess.run(
            run_command,
            capture_output=True,  # Çıktıları yakala (stdout ve stderr)
            text=True,            # Çıktıyı string olarak al
            cwd=base_dir  
        )
        
        # --- 5. COVERAGE RAPORUNU JSON OLARAK ÇIKAR ---
        # Coverage çalıştıysa veritabanı (.coverage) oluşmuştur
        # Şimdi bu veritabanını JSON formatına çevir
        json_command = [sys.executable, "-m", "coverage", "json", "-o", "coverage.json"]
        subprocess.run(json_command, capture_output=True, text=True, cwd=base_dir)

        # --- 6. SONUÇLARI ANALİZ ET ---
        # JSON raporu var mı kontrol et
        if not os.path.exists(json_path):
            # Rapor dosyası yoksa, test hiç çalışamamış demektir
            # Hatayı kullanıcıya ham haliyle göster (debug için)
            return None, f"⚠️ Testler Başlatılamadı!\n\nPython Hata Çıktısı:\n{process.stderr}\n\nStandart Çıktı:\n{process.stdout}"

        # JSON raporunu oku
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Raporun içinde app.py dosyasını bul
        # Coverage.py, dosya yollarını tam yol olarak kaydeder
        target_key = None
        for key in data["files"].keys():
            if "app.py" in key:
                target_key = key
                break
        
        # app.py bulunamazsa hata döndür
        if not target_key:
            return None, "Rapor oluştu ama kaynak kod (app.py) içinde bulunamadı."

        # app.py'nin coverage verilerini al
        file_data = data["files"][target_key]
        summary = file_data["summary"]  # Özet istatistikler
        
        # Test başarılı mı kontrol et
        # Unittest çıktısında "OK" varsa tüm testler geçmiş demektir
        is_success = "OK" in process.stderr or "OK" in process.stdout
        
        # Sonuç sözlüğünü oluştur
        output = {
            "total_tests": "Otomatik",  # Unittest otomatik sayar
            "failures": 0,              # Başarısız test sayısı (şimdilik 0)
            "errors": 0,                # Hata sayısı (şimdilik 0)
            "coverage_percent": round(summary["percent_covered"], 2),  # Coverage yüzdesi
            "missed_lines": file_data["missing_lines"],  # Test edilmeyen satır numaraları
            "success": is_success  # Testler başarılı mı?
        }
        
        return output, None

    except Exception as e:
        # Beklenmeyen hataları yakala ve detaylı hata mesajı döndür
        import traceback
        return None, f"Sistem Hatası: {str(e)}\n{traceback.format_exc()}"