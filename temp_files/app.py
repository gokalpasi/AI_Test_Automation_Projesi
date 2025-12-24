"""
E-Ticaret Sipariş Yönetim Sistemi
Bu modül, ürün, kullanıcı ve sipariş yönetimi için temel sınıfları içerir.
Test otomasyonu için örnek bir uygulama olarak kullanılmaktadır.
"""

class Urun:
    """
    Ürün sınıfı: E-ticaret sistemindeki ürünleri temsil eder.
    
    Attributes:
        isim (str): Ürün adı
        fiyat (float): Ürün birim fiyatı
        stok (int): Mevcut stok miktarı
    """
    def __init__(self, isim, fiyat, stok):
        """
        Ürün nesnesi oluşturur.
        
        Args:
            isim: Ürün adı
            fiyat: Birim fiyatı
            stok: Başlangıç stok miktarı
        """
        self.isim = isim
        self.fiyat = fiyat
        self.stok = stok

class Kullanici:
    """
    Kullanıcı sınıfı: Sistemdeki müşterileri temsil eder.
    
    Attributes:
        isim (str): Kullanıcı adı
        is_vip (bool): VIP müşteri olup olmadığı (indirim hakkı için)
    """
    def __init__(self, isim, is_vip=False):
        """
        Kullanıcı nesnesi oluşturur.
        
        Args:
            isim: Kullanıcı adı
            is_vip: VIP müşteri statüsü (varsayılan: False)
        """
        self.isim = isim
        self.is_vip = is_vip

class SiparisYoneticisi:
    """
    Sipariş yönetim sınıfı: Sipariş oluşturma, indirim hesaplama ve
    stok yönetimi işlemlerini gerçekleştirir.
    
    Attributes:
        siparis_gecmisi (list): Tamamlanan siparişlerin kayıt listesi
    """
    def __init__(self):
        """
        Sipariş yöneticisi nesnesi oluşturur.
        Sipariş geçmişi listesi boş olarak başlatılır.
        """
        self.siparis_gecmisi = []

    def siparis_olustur(self, kullanici, urun, adet):
        """
        Yeni bir sipariş oluşturur, indirimleri hesaplar ve stoktan düşer.
        
        Bu fonksiyon şu işlemleri gerçekleştirir:
        1. Sipariş validasyonu (adet ve stok kontrolü)
        2. Fiyat hesaplama (indirimler dahil)
        3. Stok güncelleme
        4. Sipariş kaydı oluşturma
        
        Args:
            kullanici (Kullanici): Sipariş veren kullanıcı
            urun (Urun): Sipariş edilen ürün
            adet (int): Sipariş edilen ürün miktarı
            
        Returns:
            dict: Sipariş kaydı (müşteri, ürün, ödenen tutar, durum)
            
        Raises:
            ValueError: Adet 0 veya negatif ise
            Exception: Yetersiz stok durumunda
        """
        # --- 1. VALİDASYON KONTROLLERİ ---
        # Adet kontrolü: Sipariş adedi pozitif olmalı
        if adet <= 0:
            raise ValueError("Sipariş adedi 0'dan büyük olmalıdır.")
        
        # Stok kontrolü: İstenen miktar mevcut stoktan fazla olamaz
        if urun.stok < adet:
            raise Exception(f"Yetersiz stok! Mevcut: {urun.stok}, İstenen: {adet}")

        # --- 2. FİYAT HESAPLAMA ---
        # Taban fiyat: Birim fiyat * adet
        taban_fiyat = urun.fiyat * adet
        indirim_orani = 0  # Toplam indirim oranı (0.0 - 1.0 arası)

        # VIP Müşteri İndirimi: VIP müşteriler %20 indirim alır
        if kullanici.is_vip:
            indirim_orani += 0.20
        
        # Tutar Bazlı İndirim: 5000 TL ve üzeri siparişlerde ekstra %10 indirim
        # Not: VIP müşteri + yüksek tutar = %30 toplam indirim
        if taban_fiyat >= 5000:
            indirim_orani += 0.10

        # --- 3. SON FİYAT VE STOK GÜNCELLEME ---
        # İndirimli fiyat hesaplama: Taban fiyat * (1 - indirim_orani)
        son_fiyat = taban_fiyat * (1 - indirim_orani)
        
        # Stoktan düşme işlemi (yan etki - side effect)
        # Bu işlem ürün nesnesinin stok değerini kalıcı olarak değiştirir
        urun.stok -= adet

        # --- 4. SİPARİŞ KAYDI OLUŞTURMA ---
        # Sipariş bilgilerini sözlük formatında kaydet
        kayit = {
            "musteri": kullanici.isim,
            "urun": urun.isim,
            "odenen_tutar": son_fiyat,
            "durum": "ONAYLANDI"
        }
        # Sipariş geçmişine ekle
        self.siparis_gecmisi.append(kayit)
        
        return kayit