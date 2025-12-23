import matplotlib.pyplot as plt
import numpy as np

def draw_guaranteed_kiviyat():
    # --- SENİN PROJENİN PUANLARI ---
    labels = [
        'Sürdürülebilirlik\n(Bakım Kolaylığı)', 
        'Yorum Oranı\n(Belgeleme)', 
        'Düşük Karmaşıklık\n(Basitlik)', 
        'Okunabilirlik\n(Halstead)', 
        'Fonksiyon Yapısı\n(Modülerlik)'
    ]
    
    # Puanları 100 üzerinden normalize ediyoruz
    stats = [
        74.79,           # Sürdürülebilirlik (A Sınıfı)
        (23.8/30)*100,   # Yorum Oranı (%30 ideal kabul edilir)
        100 - (13 * 2),  # Karmaşıklık (Düşük olması iyidir)
        100 - (2.4 * 5), # Zorluk (Düşük olması iyidir)
        100 - (9.3 * 2)  # Fonksiyon Uzunluğu (Kısa olması iyidir)
    ]
    
    # Negatif değerleri 0'a çekelim (Garanti olsun)
    stats = [max(0, s) for s in stats]

    # --- ÇİZİM MOTORU ---
    stats = np.concatenate((stats,[stats[0]])) # Grafiği kapat
    angles = np.linspace(0, 2*np.pi, len(labels), endpoint=False)
    angles = np.concatenate((angles,[angles[0]])) # Açıyı kapat

    fig, ax = plt.subplots(figsize=(7, 7), subplot_kw=dict(polar=True))
    
    # Çizgi ve Dolgu Rengi (Koyu Mavi - Profesyonel)
    ax.plot(angles, stats, 'o-', linewidth=2, color='#003366')
    ax.fill(angles, stats, alpha=0.25, color='#003366')
    
    # Etiket Ayarları
    ax.set_thetagrids(angles[:-1] * 180/np.pi, labels, fontsize=10, fontweight='bold')
    ax.set_ylim(0, 100) # Ölçek 0-100 arası
    
    plt.title('AI Test Otomasyonu - Kod Kalite Analizi', size=14, y=1.1, color='navy')
    
    # Kaydet
    plt.savefig("Proje_Kiviyat_Grafigi.png", dpi=300) # Yüksek kalite kaydet
    print("✅ Grafik oluşturuldu: Proje_Kiviyat_Grafigi.png")
    plt.show()

if __name__ == "__main__":
    draw_guaranteed_kiviyat()