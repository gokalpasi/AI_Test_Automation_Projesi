import unittest
from unittest.mock import MagicMock, patch
import pandas as pd

# Projenin modüllerini import ediyoruz
# Not: Dosya yollarının doğru olduğundan emin olun
from modules.agent import AutoTestAgent
from modules.genetic_brain import GeneticOptimizer
from modules.metrics import calculate_metrics

class ProjectWhiteBoxTests(unittest.TestCase):
    """
    Bu test seti, projenin KENDİ kaynak kodlarının (Agent, Genetic, Metrics)
    iç mantığını doğrular (White Box Testing).
    """

    # =========================================================================
    # TEST CASE 1: RL Ajanı Durum Karar Mekanizması (Decision Logic Testing)
    # Amaç: 'agent.py' içindeki _determine_state fonksiyonunun tüm if/elif
    # dallanmalarını (path coverage) doğru takip edip etmediğini ölçmek.
    # =========================================================================
    def test_agent_state_determination_logic(self):
        print("\n[WhiteBox] Test 1: RL Ajanı Durum Mantığı Kontrol Ediliyor...")
        
        # Ajanı sanal olarak başlat (Source code önemsiz burada)
        agent = AutoTestAgent(source_code="pass")
        
        # Senaryo 1: Hata varsa -> DURUM_SYNTAX_HATA dönmeli
        # (Branch 1 kontrolü)
        state = agent._determine_state(result=None, error_msg="Syntax Error", current_coverage=0)
        self.assertEqual(state, "DURUM_SYNTAX_HATA", "Hata durumu yanlış sınıflandırıldı.")

        # Senaryo 2: Başarısız Test -> DURUM_TEST_BASARISIZ dönmeli
        # (Branch 2 kontrolü)
        mock_fail_result = {'success': False, 'coverage_percent': 50}
        state = agent._determine_state(result=mock_fail_result, error_msg="", current_coverage=0)
        self.assertEqual(state, "DURUM_TEST_BASARISIZ", "Başarısız test durumu yanlış sınıflandırıldı.")

        # Senaryo 3: %100 Coverage -> DURUM_MUKEMMEL dönmeli
        # (Branch 3 kontrolü)
        mock_perfect_result = {'success': True, 'coverage_percent': 100}
        state = agent._determine_state(result=mock_perfect_result, error_msg="", current_coverage=90)
        self.assertEqual(state, "DURUM_MUKEMMEL", "Mükemmel durum yanlış sınıflandırıldı.")

        # Senaryo 4: Orta Coverage (%60) -> DURUM_COV_ORTA dönmeli
        # (Branch 4 kontrolü - Binning Logic)
        mock_mid_result = {'success': True, 'coverage_percent': 60}
        state = agent._determine_state(result=mock_mid_result, error_msg="", current_coverage=50)
        self.assertEqual(state, "DURUM_COV_ORTA", "Orta coverage dilimi yanlış hesaplandı.")

    # =========================================================================
    # TEST CASE 2: Genetik Algoritma Fitness Fonksiyonu (Integration Testing)
    # Amaç: 'genetic_brain.py' içindeki evaluate fonksiyonunun, coverage aracıyla
    # doğru haberleşip puanı (fitness score) doğru döndürdüğünü doğrulamak.
    # =========================================================================
    @patch('modules.genetic_brain.run_coverage_analysis') # Dış bağımlılığı mockluyoruz
    def test_genetic_fitness_calculation(self, mock_coverage_tool):
        print("[WhiteBox] Test 2: Genetik Algoritma Fitness Fonksiyonu Kontrol Ediliyor...")
        
        optimizer = GeneticOptimizer(source_code="pass", initial_test_code="pass")

        # Senaryo 1: Kod çalışmazsa (Success: False) -> Puan -100 olmalı
        # White Box Mantığı: 'if not result.get("success")' satırını test ediyoruz.
        mock_coverage_tool.return_value = ({'success': False, 'coverage_percent': 0}, None)
        
        _, score = optimizer.evaluate("bozuk_kod")
        self.assertEqual(score, -100, "Çalışmayan kod cezalandırılmadı (Beklenen: -100).")
        
        # Senaryo 2: Kod çalışırsa -> Puan coverage oranı olmalı
        # White Box Mantığı: 'else' bloğunu test ediyoruz.
        mock_coverage_tool.return_value = ({'success': True, 'coverage_percent': 85}, None)
        
        _, score = optimizer.evaluate("saglam_kod")
        self.assertEqual(score, 85, "Coverage puanı fitness skoruna doğru yansımadı.")

    # =========================================================================
    # TEST CASE 3: Metrik Hesaplama Motoru (Statement Testing)
    # Amaç: 'metrics.py' modülünün satır sayma ve yorum ayıklama mantığının
    # matematiksel doğruluğunu test etmek.
    # =========================================================================
    def test_metrics_calculation_accuracy(self):
        print("[WhiteBox] Test 3: Metrik Hesaplama Motoru Kontrol Ediliyor...")
        
        # Test için sanal bir kod bloğu oluşturuyoruz
        dummy_code = """
import os
# Bu bir yorum satırıdır
def test_func():
    return True
        """
        # Beklenen: 5 toplam satır, 1 yorum satırı, 1 boş satır (string başı/sonu)
        
        df, error = calculate_metrics(dummy_code)
        
        self.assertIsNone(error, "Metrik hesaplama hata verdi.")
        
        # DataFrame içindeki değerleri kontrol et
        # White Box Mantığı: calculate_metrics içindeki 'split' ve 'len' mantığını sınıyoruz.
        metrics_dict = dict(zip(df['Metrik'], df['Değer']))
        
        # Yorum satırı sayısı kontrolü
        self.assertEqual(metrics_dict['Yorum Satırı Sayısı'], 1, "Yorum satırları yanlış sayıldı.")
        
        # Fonksiyon sayısı kontrolü (AST analizi testi)
        self.assertEqual(metrics_dict['Fonksiyon Sayısı'], 1, "Fonksiyon sayısı (AST) yanlış hesaplandı.")

if __name__ == '__main__':
    unittest.main()