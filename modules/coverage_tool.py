import subprocess
import os
import json
import sys
import shutil

def run_coverage_analysis(source_code, test_code):
    """
    Testleri en standart yöntemle (module-based) çalıştırır.
    Dosya isimleri: app.py ve test_app.py olarak sabitlenir.
    Bu yöntem import ve path sorunlarını ortadan kaldırır.
    """
    # 1. Klasör Temizliği (Eski dosyalardan kurtulalım)
    if os.path.exists("temp_files"):
        try:
            shutil.rmtree("temp_files") # Klasörü içindekilerle sil
        except:
            pass # Silinemezse (dosya açıksa) devam et
            
    if not os.path.exists("temp_files"):
        os.makedirs("temp_files")

    base_dir = os.path.abspath("temp_files")
    
    # Standart isimlendirme kullanıyoruz
    source_filename = "app.py"
    test_filename = "test_app.py"
    
    source_path = os.path.join(base_dir, source_filename)
    test_path = os.path.join(base_dir, test_filename)
    json_path = os.path.join(base_dir, "coverage.json")
    
    try:
        # --- 2. Dosyaları Yaz ---
        # Kaynak Kod
        with open(source_path, "w", encoding="utf-8") as f:
            f.write(source_code)
            
        # Test Kodu
        # Import işlemini garanti altına al: 'from app import *'
        # Kodun başına bunu ekliyoruz ki test dosyası app.py'yi görsün.
        import_line = "from app import *"
        
        if "from app import" not in test_code and "import app" not in test_code:
            final_test_code = f"{import_line}\n{test_code}"
        else:
            final_test_code = test_code

        with open(test_path, "w", encoding="utf-8") as f:
            f.write(final_test_code)

        # --- 3. Komut Hazırlığı ---
        # Yöntem: 'python -m coverage run -m unittest test_app'
        # Dosya yolu yerine modül ismi kullanmak (test_app) hataları engeller.
        
        run_command = [
            sys.executable, "-m", "coverage", "run",
            "--source=app",  # Sadece app.py dosyasını takip et
            "-m", "unittest",
            "test_app"       # test_app.py dosyasını çalıştır
        ]
        
        # --- 4. Çalıştır ---
        # cwd=base_dir ile işlemi temp_files klasörünün İÇİNDE yapıyoruz
        process = subprocess.run(
            run_command,
            capture_output=True,
            text=True,
            cwd=base_dir  
        )
        
        # --- 5. Raporu JSON Olarak Çıkar ---
        # Coverage çalıştıysa veritabanı oluşmuştur, şimdi onu okuyalım
        json_command = [sys.executable, "-m", "coverage", "json", "-o", "coverage.json"]
        subprocess.run(json_command, capture_output=True, text=True, cwd=base_dir)

        # --- 6. Sonuçları Analiz Et ---
        if not os.path.exists(json_path):
            # Eğer rapor dosyası yoksa, test hiç çalışamamış demektir.
            # Hatayı kullanıcıya ham haliyle gösterelim ki sebebini anlayalım.
            return None, f"⚠️ Testler Başlatılamadı!\n\nPython Hata Çıktısı:\n{process.stderr}\n\nStandart Çıktı:\n{process.stdout}"

        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Raporun içinde app.py dosyasını bul
        target_key = None
        for key in data["files"].keys():
            if "app.py" in key:
                target_key = key
                break
        
        if not target_key:
            return None, "Rapor oluştu ama kaynak kod (app.py) içinde bulunamadı."

        file_data = data["files"][target_key]
        summary = file_data["summary"]
        
        # Unittest çıktısında "OK" varsa başarılıdır
        is_success = "OK" in process.stderr or "OK" in process.stdout
        
        output = {
            "total_tests": "Otomatik", 
            "failures": 0, 
            "errors": 0,
            "coverage_percent": round(summary["percent_covered"], 2),
            "missed_lines": file_data["missing_lines"],
            "success": is_success
        }
        
        return output, None

    except Exception as e:
        import traceback
        return None, f"Sistem Hatası: {str(e)}\n{traceback.format_exc()}"