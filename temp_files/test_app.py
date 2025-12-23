import unittest
from app import Urun, Kullanici, SiparisYoneticisi

class TestSiparisYoneticisi(unittest.TestCase):
    
    def setUp(self):
        # Baba ve Anne Koddan alınan temiz setUp
        self.manager = SiparisYoneticisi()
        self.laptop = Urun("Gaming Laptop", 10000, 5) # Fiyat: 10.000, Stok: 5
        self.normal_user = Kullanici("Ahmet", is_vip=False)
        self.vip_user = Kullanici("Ayşe", is_vip=True)

    # TEST 1: Başarılı sipariş ve stok düşüşü kontrolü (Baba Koddan tamamlama)
    def test_basarili_siparis_stok_dususu(self):
        # 1 adet laptop alınıyor
        self.manager.siparis_olustur(self.normal_user, self.laptop, 1)
        
        # Stok 5'ten 4'e düşmüş olmalı.
        beklenen_stok = 4
        gerceklese_stok = self.laptop.stok
        self.assertEqual(gerceklese_stok, beklenen_stok, "Stok doğru şekilde düşmedi!")

    # TEST 2: Yetersiz stok hatası kontrolü (Baba Koddan alınan Exception yakalama)
    def test_yetersiz_stok_hatasi(self):
        # Stokta 5 tane var, 6 tane istemeye çalışıyoruz.
        istenilen_adet = 6
        
        # Bu işlemin bir hata fırlatması gerekiyor.
        with self.assertRaises(Exception):
            self.manager.siparis_olustur(self.normal_user, self.laptop, istenilen_adet)

    # TEST 3: VIP ve Yüksek Tutar indiriminin birlikte çalışması (Baba Koddan alınan beklenen değer, Anne Koddan alınan doğru assert)
    def test_vip_ve_tutar_indirimi(self):
        # Senaryo: %30 indirim (10.000 * 0.7 = 7000.0 TL)
        sonuc = self.manager.siparis_olustur(self.vip_user, self.laptop, 1)
        
        # Beklenen fiyatı hesaplayın ve doğrulayın.
        beklenen_fiyat = 7000.0 
        self.assertEqual(sonuc["odenen_tutar"], beklenen_fiyat, "VIP + Tutar indirimi yanlış hesaplandı!")

    # TEST 4: Negatif adet kontrolü (Baba Koddan tamamlama)
    def test_negatif_adet(self):
        # -1 adet sipariş verilirse 'ValueError' fırlatılmalı.
        with self.assertRaises(ValueError):
            self.manager.siparis_olustur(self.normal_user, self.laptop, -1)

if __name__ == '__main__':
    import unittest
    unittest.main(argv=['first-arg-is-ignored'], exit=False)