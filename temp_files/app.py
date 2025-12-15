class AkilliKasa:
    def __init__(self):
        self.kilitli = True
        self.bakiye = 0
        self.ozel_anahtar = "SÜPER_GİZLİ_ANAHTAR_2025"

    def islem_yap(self, komut, miktar=0, anahtar=None):
        """
        RL Ajanını zorlamak için tasarlanmış fonksiyon.
        Yanlış veri tiplerinde hata fırlatır (Ceza puanı için).
        """
        # TUZAK 1: Veri Tipi Kontrolü (Ajan bunu başta yanlış yapabilir)
        if not isinstance(komut, str):
            raise TypeError("Komut bir metin olmalidir!")

        # TUZAK 2: Negatif Miktar (Mantık Hatası)
        if isinstance(miktar, (int, float)) and miktar < 0:
            raise ValueError("Miktar negatif olamaz!")

        # ŞİFRE AÇMA (Basit Durum)
        if komut == "AC":
            self.kilitli = False
            return "Kasa Acildi"

        # PARA YATIRMA (Kilit Kontrolü)
        elif komut == "YATIR":
            if self.kilitli:
                return "Kasa Kilitli!"
            self.bakiye += miktar
            return self.bakiye

        # GİZLİ DURUM (Coverage Arttırma Stratejisi Gerektirir)
        elif komut == "SIFIRLA":
            # Ajanın bu 'if' bloğuna girmesi için doğru anahtarı bulması lazım
            # İlk denemede muhtemelen burayı test edemeyecek ve 'STRATEJI_GENISLET' seçecek.
            if anahtar == self.ozel_anahtar:
                self.bakiye = 0
                return "Sifirlandi"
            else:
                return "Yetkisiz Islem"
        
        else:
            return "Gecersiz Komut"