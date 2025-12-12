import radon.complexity as cc
from radon.metrics import mi_visit, h_visit
import ast

def calculate_metrics(code_string):
    """
    Verilen Python kodu için genişletilmiş metrikleri hesaplar.
    """
    metrics = {}
    error = None

    try:
        # 1. Temel Satır Analizleri
        lines = code_string.split('\n')
        total_loc = len(lines)
        empty_lines = len([l for l in lines if not l.strip()])
        comment_lines = len([l for l in lines if l.strip().startswith('#')])
        
        # Mantıksal Satır Sayısı (LLOC) - Boşluk ve yorum hariç kod
        lloc = total_loc - empty_lines - comment_lines

        # 2. Radon Kütüphanesi ile Analizler (Karmaşıklık ve Bakım)
        # Sürdürülebilirlik İndeksi (0-100 arası)
        maintainability = mi_visit(code_string, multi=True)
        
        # Döngüsel Karmaşıklık (Cyclomatic Complexity)
        complexity_blocks = cc.cc_visit(code_string)
        total_cc = sum([block.complexity for block in complexity_blocks])
        avg_cc = total_cc / len(complexity_blocks) if complexity_blocks else 0
        
        # En karmaşık fonksiyonu bulma
        max_cc_block = max(complexity_blocks, key=lambda x: x.complexity) if complexity_blocks else None
        max_cc_name = f"{max_cc_block.name} ({max_cc_block.complexity})" if max_cc_block else "Yok"

        # 3. YENİ: AST (Soyut Sözdizimi Ağacı) ile Yapısal Analiz
        tree = ast.parse(code_string)
        
        # Sınıf ve Fonksiyon Sayıları
        class_count = len([node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)])
        function_count = len([node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)])
        
        # Test Fonksiyonu Sayısı (İsmi 'test_' ile başlayanlar)
        test_count = len([node for node in ast.walk(tree) 
                          if isinstance(node, ast.FunctionDef) and node.name.startswith('test_')])

        # 4. YENİ: Hesaplamalı Metrikler
        
        # Yorum Oranı (%)
        comment_ratio = (comment_lines / total_loc * 100) if total_loc > 0 else 0
        
        # Ortalama Fonksiyon Uzunluğu (Satır)
        avg_func_len = (lloc / function_count) if function_count > 0 else 0

        # Halstead Metrikleri (Zorluk Seviyesi)
        # Radon h_visit kullanıyoruz
        halstead_metrics = h_visit(code_string)
        difficulty = halstead_metrics.total.difficulty # Kodun anlaşılma zorluğu

        # --- SONUÇLARI SÖZLÜĞE EKLE ---
        metrics["Toplam Satır (LOC)"] = total_loc
        metrics["Mantıksal Satır (LLOC)"] = lloc
        metrics["Yorum Satırı Sayısı"] = comment_lines
        metrics["Yorum Oranı (%)"] = f"%{comment_ratio:.1f}"  # YENİ
        
        metrics["Sınıf Sayısı"] = class_count # YENİ
        metrics["Fonksiyon Sayısı"] = function_count # YENİ
        metrics["Test Senaryosu Sayısı"] = test_count # YENİ
        metrics["Ort. Fonksiyon Uzunluğu"] = f"{avg_func_len:.1f} satır" # YENİ

        metrics["Sürdürülebilirlik Puanı"] = f"{maintainability:.2f} ({_get_rank(maintainability)})"
        metrics["Toplam Karmaşıklık (CC)"] = total_cc
        metrics["Ortalama Karmaşıklık"] = f"{avg_cc:.2f}"
        metrics["En Karmaşık Yapı"] = max_cc_name
        metrics["Halstead Zorluk Puanı"] = f"{difficulty:.2f}" # YENİ

    except Exception as e:
        error = str(e)

    # DataFrame'e çevirmek için pandas'a uygun formatta döndür
    import pandas as pd
    df = pd.DataFrame(list(metrics.items()), columns=["Metrik", "Değer"])
    
    return df, error

def _get_rank(score):
    """Sürdürülebilirlik puanına göre harf notu verir."""
    if score >= 20: return "A (Mükemmel)"
    elif score >= 10: return "B (İyi)"
    else: return "C (Kötü - Refactor Gerekli)"