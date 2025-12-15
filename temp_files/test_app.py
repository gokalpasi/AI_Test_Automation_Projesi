import unittest
# Hedef sınıfın 'app' dosyasında bulunduğunu varsayıyoruz.
from app import AkilliKasa

class TestAkilliKasa(unittest.TestCase):
    """AkilliKasa sınıfının fonksiyonelliğini ve tuzağa yönelik hata yakalama yeteneğini test eder."""

    def setUp(self):
        """Her testten önce yeni bir kasa örneği oluşturur."""
        self.kasa = AkilliKasa()
        self.GIZLI_ANAHTAR = "SÜPER_GİZLİ_ANAHTAR_2025" # Testler için sabit anahtar

    # --- Başlangıç Durumu Testleri ---
    def test_initial_state(self):
        """Kasanın başlangıçta kilitli olduğunu ve bakiyenin sıfır olduğunu doğrular."""
        self.assertTrue(self.kasa.kilitli)
        self.assertEqual(self.kasa.bakiye, 0)

    # --- Komut AC (Açma) Testleri ---
    def test_ac_komutu_success(self):
        """Kasanın başarıyla açıldığını ve kilit durumunun değiştiğini doğrular."""
        result = self.kasa.islem_yap("AC")
        self.assertEqual(result, "Kasa Acildi")
        self.assertFalse(self.kasa.kilitli)

    # --- Hata/Tuzak Testleri ---
    def test_tuzak1_type_error_on_komut(self):
        """Komutun dize (string) olmaması durumunda TypeError fırlattığını kontrol eder."""
        with self.assertRaisesRegex(TypeError, "Komut bir metin olmalidir!"):
            self.kasa.islem_yap(komut=123)

    def test_tuzak2_value_error_on_negative_miktar(self):
        """Miktarın negatif olması durumunda ValueError fırlattığını kontrol eder."""
        # Negatif miktarı int olarak test et
        with self.assertRaisesRegex(ValueError, "Miktar negatif olamaz!"):
            self.kasa.islem_yap(komut="YATIR", miktar=-10)
        
        # Negatif miktarı float olarak test et
        with self.assertRaisesRegex(ValueError, "Miktar negatif olamaz!"):
            self.kasa.islem_yap(komut="YATIR", miktar=-5.5)

    # --- Komut YATIR Testleri ---
    def test_yatir_kilitli_iken(self):
        """Kasa kilitliyken para yatırma girişiminin başarısız olduğunu kontrol eder."""
        self.assertTrue(self.kasa.kilitli)
        result = self.kasa.islem_yap("YATIR", miktar=100)
        self.assertEqual(result, "Kasa Kilitli!")
        self.assertEqual(self.kasa.bakiye, 0) # Bakiye değişmemeli

    def test_yatir_acik_iken_integer(self):
        """Kasa açıkken tam sayı miktarın başarıyla yatırıldığını kontrol eder."""
        self.kasa.islem_yap("AC")
        result = self.kasa.islem_yap("YATIR", miktar=500)
        self.assertEqual(result, 500)
        self.assertEqual(self.kasa.bakiye, 500)

    def test_yatir_acik_iken_float_ve_toplam(self):
        """Kasa açıkken küsuratlı miktarların doğru toplandığını kontrol eder."""
        self.kasa.islem_yap("AC")
        self.kasa.islem_yap("YATIR", miktar=10.50)
        result = self.kasa.islem_yap("YATIR", miktar=9.50)
        self.assertEqual(result, 20.00)
        self.assertEqual(self.kasa.bakiye, 20.00)
    
    def test_yatir_sifir_miktar(self):
        """Sıfır miktarın yatırılmasının bakiyeyi değiştirmemesi gerektiğini kontrol eder."""
        self.kasa.islem_yap("AC")
        self.kasa.islem_yap("YATIR", miktar=100)
        self.kasa.islem_yap("YATIR", miktar=0)
        self.assertEqual(self.kasa.bakiye, 100)

    # --- Komut SIFIRLA (Gizli Durum) Testleri ---
    def test_sifirla_yetkisiz(self):
        """Yanlış anahtarla sıfırlama girişiminin yetkisiz işlem döndürdüğünü kontrol eder."""
        self.kasa.islem_yap("AC")
        self.kasa.islem_yap("YATIR", miktar=1000)
        
        result = self.kasa.islem_yap("SIFIRLA", anahtar="YANLIS_ANAHTAR")
        self.assertEqual(result, "Yetkisiz Islem")
        self.assertEqual(self.kasa.bakiye, 1000) # Bakiye sıfırlanmamalı

    def test_sifirla_yetkili_basarili(self):
        """Doğru anahtarla sıfırlama girişiminin başarılı olduğunu ve bakiyeyi sıfırladığını kontrol eder."""
        self.kasa.islem_yap("AC")
        self.kasa.islem_yap("YATIR", miktar=555)

        result = self.kasa.islem_yap("SIFIRLA", anahtar=self.GIZLI_ANAHTAR)
        self.assertEqual(result, "Sifirlandi")
        self.assertEqual(self.kasa.bakiye, 0)

    # --- Geçersiz Komut Testi ---
    def test_gecersiz_komut(self):
        """Tanımlanmamış bir komutun geçersiz komut mesajını döndürdüğünü kontrol eder."""
        result = self.kasa.islem_yap("CEK")
        self.assertEqual(result, "Gecersiz Komut")
        
        result = self.kasa.islem_yap("12345")
        self.assertEqual(result, "Gecersiz Komut")


if __name__ == '__main__':
    unittest.main()