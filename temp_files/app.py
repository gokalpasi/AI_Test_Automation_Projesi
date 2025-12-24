"""
E-Ticaret Sipariş Yönetim Sistemi (Test Edilebilir Modül)

Bu modül; ürün, kullanıcı ve sipariş süreçlerini yöneten temel iş mantığını barındırır.
Otomatik test üretimi için 'Boundary Value Analysis' ve 'Logic Path Testing'
uygulamalarına uygun yapıdadır.
"""

class Urun:
    """
    Ürün varlık sınıfı (Entity Class): Sistemdeki envanter verilerini temsil eder.

    Attributes:
        isim (str): Ürün tanımlayıcı adı.
        fiyat (float): Birim satış bedeli.
        stok (int): Satılabilir mevcut miktar.
    """
    def __init__(self, isim, fiyat, stok):
        """
        Yeni bir ürün nesnesi ilklendirir.

        Args:
            isim: Ürün adı.
            fiyat: Sayısal birim fiyat (Testlerde negatif/sıfır değerler kontrol edilmelidir).
            stok: Tam sayı stok miktarı.
        """
        self.isim = isim
        self.fiyat = fiyat
        self.stok = stok

class Kullanici:
    """
    Kullanıcı profili sınıfı: Müşteri tipine göre davranışsal farklılıkları yönetir.

    Attributes:
        isim (str): Kullanıcı kimlik adı.
        is_vip (bool): True ise VIP indirim mantığını tetikler.
    """
    def __init__(self, isim, is_vip=False):
        """
        Kullanıcı nesnesini tanımlar.

        Args:
            isim: Müşteri adı.
            is_vip: VIP statüsü (Varsayılan: False).
        """
        self.isim = isim
        self.is_vip = is_vip

class SiparisYoneticisi:
    """
    Sipariş Yönetim Motoru (Business Logic Layer):
    Hesaplama, doğrulama ve veri mutasyonu işlemlerini yürüten merkezi sınıf.

    Attributes:
        siparis_gecmisi (list): Tüm başarılı işlem kayıtlarını tutan koleksiyon.
    """
    def __init__(self):
        """
        Yönetici nesnesini boş bir geçmiş listesiyle başlatır.
        """
        self.siparis_gecmisi = []

    def siparis_olustur(self, kullanici, urun, adet):
        """
        Sipariş yaşam döngüsünü yöneten ana işleme fonksiyonu.

        Süreç Akışı (Logic Flow):
        1. Input Validation: Adet ve stok sınır değer kontrolü.
        2. Pricing Logic: VIP ve Tutar bazlı kümülatif indirim hesaplama.
        3. State Update: Ürün stok objesinin mutasyonu.
        4. Logging: Siparişin geçmişe kaydedilmesi.

        Args:
            kullanici (Kullanici): İşlemi gerçekleştiren aktör.
            urun (Urun): Satın alınan ürün referansı.
            adet (int): Talep edilen miktar.

        Returns:
            dict: İşlem özeti (İndirim uygulanmış tutar ve durum bilgisi dahil).

        Raises:
            ValueError: 'adet <= 0' durumu (Girdi doğrulama hatası).
            Exception: 'stok < adet' durumu (İş kuralı ihlali).
        """

        # --- 1. GİRDİ DOĞRULAMA (Validation) ---
        # Negatif veya sıfır adetli siparişler engellenmelidir (Boundary Case)
        if adet <= 0:
            raise ValueError("Sipariş adedi 0'dan büyük olmalıdır.")

        # Stok yetersizliği kontrolü (Negative Path Testing)
        if urun.stok < adet:
            raise Exception(f"Yetersiz stok! Mevcut: {urun.stok}, İstenen: {adet}")

        # --- 2. DİNAMİK İNDİRİM HESAPLAMA (Pricing Engine) ---
        taban_fiyat = urun.fiyat * adet
        indirim_orani = 0  # Kümülatif indirim payı

        # Karar Yapısı: VIP İndirimi (%20)
        if kullanici.is_vip:
            indirim_orani += 0.20

        # Karar Yapısı: Hacimsel İndirim (5000 TL ve üzeri için ekstra %10)
        # Not: İki 'if' bağımsızdır; VIP olan ve 5000 TL aşan müşteri %30 indirim alır.
        if taban_fiyat >= 5000:
            indirim_orani += 0.10

        # --- 3. VERİ GÜNCELLEME VE KAYIT ---
        # İndirimler uygulandıktan sonraki nihai ödeme tutarı
        son_fiyat = taban_fiyat * (1 - indirim_orani)

        # Stok azaltımı (Yan etki kontrolü - Side effect testing için önemli)
        urun.stok -= adet

        # Sistem çıktısını sözlük formatında hazırla
        kayit = {
            "musteri": kullanici.isim,
            "urun": urun.isim,
            "odenen_tutar": son_fiyat,
            "durum": "ONAYLANDI"
        }

        # Kalıcı geçmiş kaydı (Persistence mock-up)
        self.siparis_gecmisi.append(kayit)
        
        return kayit