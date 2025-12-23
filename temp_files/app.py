class Urun:
    def __init__(self, isim, fiyat, stok):
        self.isim = isim
        self.fiyat = fiyat
        self.stok = stok

class Kullanici:
    def __init__(self, isim, is_vip=False):
        self.isim = isim
        self.is_vip = is_vip

class SiparisYoneticisi:
    def __init__(self):
        self.siparis_gecmisi = []

    def siparis_olustur(self, kullanici, urun, adet):
        """
        Siparişi işler, indirimleri hesaplar ve stoktan düşer.
        """
        # 1. Validasyon Kontrolleri
        if adet <= 0:
            raise ValueError("Sipariş adedi 0'dan büyük olmalıdır.")
        
        if urun.stok < adet:
            raise Exception(f"Yetersiz stok! Mevcut: {urun.stok}, İstenen: {adet}")

        # 2. Fiyat Hesaplama
        taban_fiyat = urun.fiyat * adet
        indirim_orani = 0

        # VIP Müşteri İndirimi (%20)
        if kullanici.is_vip:
            indirim_orani += 0.20
        
        # Tutar Bazlı İndirim (5000 TL üzeri ise ekstra %10)
        if taban_fiyat >= 5000:
            indirim_orani += 0.10

        # 3. Son Fiyat ve Stok Güncelleme
        son_fiyat = taban_fiyat * (1 - indirim_orani)
        urun.stok -= adet  # Stoktan düşme işlemi (Side effect)

        # Sipariş Kaydı
        kayit = {
            "musteri": kullanici.isim,
            "urun": urun.isim,
            "odenen_tutar": son_fiyat,
            "durum": "ONAYLANDI"
        }
        self.siparis_gecmisi.append(kayit)
        
        return kayit