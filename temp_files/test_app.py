import unittest
from app import Urun, Kullanici, SiparisYoneticisi

class TestSiparisYoneticisi(unittest.TestCase):
    """
    Sipariş Yönetim Sistemi için Birim Test Suiti.
    Bu sınıf; stok mutasyonlarını, indirim algoritmalarını ve hata fırlatma
    mekanizmalarını (Exception Handling) doğrulamak üzere tasarlanmıştır.
    """

    def setUp(self):
        """
        Her test metodundan önce çalıştırılan hazırlık bloğu (Test Fixture).
        İzole bir test ortamı için taze nesne örnekleri oluşturur.
        """
        self.manager = SiparisYoneticisi()
        # Sınır değer analizi ve yüksek tutar indirimi için 10.000 TL'lik ürün
        self.laptop = Urun("Gaming Laptop", 10000, 5)
        self.normal_user = Kullanici("Ahmet", is_vip=False)
        self.vip_user = Kullanici("Ayşe", is_vip=True)

    def test_basarili_siparis_stok_dususu(self):
        """
        Senaryo: Geçerli girdilerle başarılı sipariş oluşturma.
        Amaç: Ürün stok miktarının (state) sipariş adedi kadar azaldığını teyit etmek.
        """
        # Aksiyon: 1 adet laptop siparişi tetiklenir
        self.manager.siparis_olustur(self.normal_user, self.laptop, 1)

        # Doğrulama: Yan etki (side effect) kontrolü
        beklenen_stok = 4
        gerceklese_stok = self.laptop.stok
        self.assertEqual(gerceklese_stok, beklenen_stok, "Hata: Sipariş sonrası stok güncellenmedi!")

    def test_yetersiz_stok_hatasi(self):
        """
        Senaryo: Mevcut stok miktarından fazla ürün talebi.
        Amaç: Sistemin 'Exception' fırlatarak işlemi durdurduğunu ve geçersiz siparişi reddettiğini ölçmek.
        """
        # Aksiyon: Stokta (5) olandan fazlası (6) talep edilir
        istenilen_adet = 6

        # Doğrulama: Beklenen hata tipinin fırlatılıp fırlatılmadığı kontrol edilir
        with self.assertRaises(Exception):
            self.manager.siparis_olustur(self.normal_user, self.laptop, istenilen_adet)

    def test_vip_ve_tutar_indirimi(self):
        """
        Senaryo: Hem VIP statüsü hem de 5000 TL üstü harcama yapan kullanıcı.
        Amaç: Kümülatif indirim mantığının (%20 + %10 = %30) doğru hesaplandığını doğrulamak.
        Hesaplama: 10.000 * (1 - 0.30) = 7.000
        """
        # Aksiyon: VIP kullanıcı yüksek tutarlı sipariş verir
        sonuc = self.manager.siparis_olustur(self.vip_user, self.laptop, 1)

        # Doğrulama: Matematiksel doğruluk kontrolü
        beklenen_fiyat = 7000.0
        self.assertEqual(sonuc["odenen_tutar"], beklenen_fiyat, "Hata: VIP + Tutar indirimi birleşik hesaplanamadı!")

    def test_negatif_adet(self):
        """
        Senaryo: Geçersiz veri girişi (Negatif miktar).
        Amaç: Girdi doğrulama katmanının (Input Validation) 'ValueError' döndürerek
        sistem tutarlılığını koruduğunu teyit etmek.
        """
        # Aksiyon: Mantıksız (-1) adet girişi yapılır
        with self.assertRaises(ValueError):
            self.manager.siparis_olustur(self.normal_user, self.laptop, -1)


if __name__ == '__main__':
    # Testleri konsol üzerinden veya Streamlit entegrasyonuyla çalıştırmak için gerekli entry point
    import unittest

    unittest.main(argv=['first-arg-is-ignored'], exit=False)