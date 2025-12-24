"""
Grafik Çizim Modülü
Bu modül, projenin kod kalite metriklerini görselleştirmek için
radar (kıvıyat) grafiği oluşturur.
"""

import matplotlib.pyplot as plt
import numpy as np

def draw_guaranteed_kiviyat():
    """
    Projenin kod kalite metriklerini radar grafiği olarak çizer ve kaydeder.
    
    Bu fonksiyon, beş farklı kalite metriğini (sürdürülebilirlik, yorum oranı,
    karmaşıklık, okunabilirlik, fonksiyon yapısı) 0-100 arası puanlarla
    normalize ederek polar (radar) grafik formatında görselleştirir.
    
    Grafik, 'Proje_Kiviyat_Grafigi.png' dosyasına yüksek çözünürlükte kaydedilir.
    """
    # --- PROJE METRİKLERİNİN ETİKETLERİ ---
    # Radar grafiğindeki her eksen için açıklayıcı etiketler
    labels = [
        'Sürdürülebilirlik\n(Bakım Kolaylığı)',  # Kodun bakımının ne kadar kolay olduğu
        'Yorum Oranı\n(Belgeleme)',              # Kod içindeki yorum satırlarının oranı
        'Düşük Karmaşıklık\n(Basitlik)',         # Kodun ne kadar basit ve anlaşılır olduğu
        'Okunabilirlik\n(Halstead)',            # Halstead metriklerine göre okunabilirlik
        'Fonksiyon Yapısı\n(Modülerlik)'         # Fonksiyonların modüler yapısı
    ]
    
    # --- METRİK PUANLARININ HESAPLANMASI ---
    # Her metrik 0-100 arası normalize edilmiş değerlerle temsil edilir
    stats = [
        74.79,           # Sürdürülebilirlik: A sınıfı puan (20+ puan A sınıfı demektir)
        (23.8/30)*100,   # Yorum Oranı: %30 ideal kabul edilir, bu değer normalize ediliyor
        100 - (13 * 2),  # Karmaşıklık: Düşük karmaşıklık yüksek puan demektir (ters orantı)
        100 - (2.4 * 5), # Zorluk: Halstead zorluk metriği, düşük olması iyidir (ters orantı)
        100 - (9.3 * 2)  # Fonksiyon Uzunluğu: Kısa fonksiyonlar tercih edilir (ters orantı)
    ]
    
    # Negatif değerleri 0'a çekelim (Grafikte negatif değer görünmesin)
    stats = [max(0, s) for s in stats]

    # --- POLAR GRAFİK HAZIRLIĞI ---
    # Radar grafiği için açıları hesapla (her metrik için eşit açı aralığı)
    # np.linspace: 0'dan 2π'ye kadar eşit aralıklı açılar oluşturur
    angles = np.linspace(0, 2*np.pi, len(labels), endpoint=False)
    
    # Grafiği kapatmak için: İlk değeri sona ekle (döngüyü tamamlamak için)
    stats = np.concatenate((stats, [stats[0]]))
    angles = np.concatenate((angles, [angles[0]]))

    # Polar (radar) grafik için figure ve axes oluştur
    # figsize=(7, 7): Kare format, polar=True: Polar koordinat sistemi
    fig, ax = plt.subplots(figsize=(7, 7), subplot_kw=dict(polar=True))
    
    # --- GRAFİK ÇİZİMİ ---
    # Çizgi grafiği: 'o-' formatı (nokta-çizgi), kalınlık 2, koyu mavi renk
    ax.plot(angles, stats, 'o-', linewidth=2, color='#003366')
    # Alan doldurma: Şeffaflık (alpha=0.25) ile alanı doldur
    ax.fill(angles, stats, alpha=0.25, color='#003366')
    
    # --- ETİKET VE ÖLÇEK AYARLARI ---
    # Açı etiketlerini ayarla: Radyanı dereceye çevir (180/π) ve etiketleri yerleştir
    ax.set_thetagrids(angles[:-1] * 180/np.pi, labels, fontsize=10, fontweight='bold')
    # Y ekseni (yarıçap) ölçeğini 0-100 arası sınırla
    ax.set_ylim(0, 100)
    
    # Grafik başlığını ayarla
    plt.title('AI Test Otomasyonu - Kod Kalite Analizi', size=14, y=1.1, color='navy')
    
    # --- DOSYAYA KAYDETME ---
    # Grafiği PNG formatında yüksek çözünürlükte (300 DPI) kaydet
    plt.savefig("Proje_Kiviyat_Grafigi.png", dpi=300)
    print("✅ Grafik oluşturuldu: Proje_Kiviyat_Grafigi.png")
    # Grafiği ekranda göster
    plt.show()

if __name__ == "__main__":
    draw_guaranteed_kiviyat()