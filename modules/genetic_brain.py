"""
Genetik Algoritma Optimizasyon Modülü
Bu modül, test kodlarını evrimsel algoritma (genetik algoritma) kullanarak
optimize eder. Doğal seçilim, mutasyon ve çaprazlama operatörleri ile
en yüksek coverage'a sahip test kodunu bulmayı hedefler.
"""

import random
import time
from modules.ai_generator import generate_test_code_from_gemini
from modules.coverage_tool import run_coverage_analysis

class GeneticOptimizer:
    """
    Genetik Algoritma ile test kodu optimizasyonu yapan sınıf.
    
    Bu sınıf, doğal seçilim prensiplerini kullanarak test kodlarını evrimleştirir:
    - Popülasyon: Birden fazla test kodu varyasyonu
    - Fitness: Coverage oranı (ne kadar yüksekse o kadar iyi)
    - Seçilim: En iyi kodlar hayatta kalır
    - Mutasyon: Rastgele değişiklikler
    - Çaprazlama: İki kodun özelliklerini birleştirme
    """
    
    def __init__(self, source_code, initial_test_code, population_size=4, generations=3):
        """
        Genetik optimizatör başlatır.
        
        Args:
            source_code: Test edilecek kaynak kod
            initial_test_code: Başlangıç test kodu (opsiyonel, boş olabilir)
            population_size: Popülasyon büyüklüğü (kaç farklı test kodu varyasyonu)
            generations: Evrim nesil sayısı (kaç nesil boyunca evrimleşecek)
        """
        self.source_code = source_code
        self.initial_test_code = initial_test_code
        self.population_size = population_size
        self.generations = generations
        self.population = []  # Popülasyon: [(test_kodu, fitness_score), ...] formatında
        
        # İstatistik: Toplam kaç test kodu değerlendirildi
        self.total_tests_run = 0 

    def initialize_population(self):
        """
        Başlangıç popülasyonunu oluşturur.
        
        Eğer başlangıç test kodu verilmişse onu kullanır, yoksa basit bir
        şablon test kodu oluşturur. Sonra mutasyon operatörü ile popülasyonu
        çeşitlendirir.
        """
        # Başlangıç test kodu yoksa basit bir şablon oluştur
        if not self.initial_test_code:
            base_code = """
import unittest
from app import *
class TestApp(unittest.TestCase):
    def test_baslangic(self):
        pass
"""
        else:
            base_code = self.initial_test_code
        
        # İlk birey: Başlangıç kodu (değerlendirilmiş)
        self.population.append(self.evaluate(base_code))
        
        # Kalan popülasyon: Mutasyon ile çeşitlendir
        for _ in range(self.population_size - 1):
            time.sleep(1)  # API rate limit için bekleme
            mutated = self.mutate(base_code)
            self.population.append(self.evaluate(mutated))

    def evaluate(self, test_code):
        """
        Fitness Fonksiyonu: Test kodunun kalitesini ölçer.
        
        Bu fonksiyon, test kodunun kaynak kodu ne kadar iyi kapsadığını
        (coverage) ölçer. Coverage oranı fitness skoru olarak kullanılır.
        
        Args:
            test_code: Değerlendirilecek test kodu (string)
            
        Returns:
            tuple: (test_kodu, fitness_score) - Fitness skoru coverage yüzdesidir
        """
        # İstatistik: Her değerlendirmede sayacı artır
        self.total_tests_run += 1
        
        try:
            # Coverage analizi çalıştır
            result, _ = run_coverage_analysis(self.source_code, test_code)
            score = result.get('coverage_percent', 0)
            
            # Eğer test başarısızsa (çalışmıyorsa) büyük ceza ver
            if not result.get('success', False):
                score = -100  # Çalışmayan kodlar elenmeli
                
            return (test_code, score)
        except Exception:
            # Hata durumunda da ceza ver
            return (test_code, -100)

    def mutate(self, test_code):
        """
        Genetik Mutasyon Operatörü: Test koduna rastgele değişiklik yapar.
        
        Mutasyon, genetik algoritmanın çeşitlilik sağlaması için kritiktir.
        Farklı mutasyon tipleri uygulanabilir:
        - Değer değiştirme
        - Yeni assertion ekleme
        - Satır silme
        - Mantık operatörlerini tersine çevirme
        
        Args:
            test_code: Mutasyona uğrayacak test kodu
            
        Returns:
            str: Mutasyona uğramış yeni test kodu
        """
        # Rastgele bir mutasyon tipi seç
        mutation_type = random.choice([
            "VALUE_MODIFICATION",  # Değer değiştirme
            "ADD_NEW_ASSERT",      # Yeni assertion ekleme
            "REMOVE_LINE",         # Satır silme
            "LOGIC_FLIP"           # Mantık operatörünü tersine çevirme
        ])
        
        # AI'ya mutasyon talimatı ver
        prompt = f"""
        Sen 'Kör' bir Genetik Mutasyon Operatörüsün.
        Görevin kodu iyileştirmek DEĞİL, sadece istenen rastgele değişikliği yapmaktır.
        Kodun çalışıp çalışmayacağını veya coverage'ı artırıp artırmayacağını umursama. Sadece değişimi uygula.
        
        Kaynak Kod (Sadece referans için):
        {self.source_code}
        
        Mevcut Test Kodu:
        {test_code}
        
        UYGULANACAK MUTASYON TİPİ: {mutation_type}
        
        Talimatlar:
        1. Eğer {mutation_type} == "VALUE_MODIFICATION": Testteki parametreleri (sayı, string) rastgele değiştir.
        2. Eğer {mutation_type} == "ADD_NEW_ASSERT": Kaynak koddaki fonksiyonlardan birine rastgele bir çağrı ekle. Mantıklı olmak zorunda değil.
        3. Eğer {mutation_type} == "REMOVE_LINE": Test fonksiyonlarından birinden rastgele bir satır sil.
        4. Eğer {mutation_type} == "LOGIC_FLIP": Kodda geçen bir mantıksal operatörü tersine çevir.
        
        Sadece geçerli Python kodu döndür. Yorum satırı ekleme.
        """
        
        return generate_test_code_from_gemini(prompt, fix_for_streamlit=True)

    def crossover(self, parent1, parent2):
        """
        Çaprazlama (Crossover) Operatörü: İki test kodunun özelliklerini birleştirir.
        
        Genetik algoritmada, iki iyi bireyin özelliklerini birleştirerek
        daha iyi bir çocuk birey oluşturma işlemidir.
        
        Args:
            parent1: İlk ebeveyn test kodu
            parent2: İkinci ebeveyn test kodu
            
        Returns:
            str: İki kodun özelliklerini harmanlayan yeni test kodu
        """
        prompt = f"""
        Genetik Çaprazlama (Crossover) yap.
        Aşağıdaki iki test kodunu al ve özelliklerini rastgele harmanlayarak yeni bir test kodu oluştur.
        
        Anne Kod:
        {parent1}
        
        Baba Kod:
        {parent2}
        """
        return generate_test_code_from_gemini(prompt, fix_for_streamlit=True)

    def evolve(self):
        """
        Ana Evrim Döngüsü: Genetik algoritmanın temel işleyişi.
        
        Bu fonksiyon şu adımları takip eder:
        1. Popülasyonu başlat
        2. Her nesil için:
           a. Seçilim: En iyi bireyleri seç
           b. Üreme: Mutasyon ve çaprazlama ile yeni nesil oluştur
           c. Elitizm: En iyi bireyi koru
        3. %100 coverage'a ulaşırsa dur
        
        Returns:
            tuple: ((en_iyi_kod, en_iyi_skor), evrim_geçmişi)
        """
        # Başlangıç popülasyonunu oluştur
        self.initialize_population()
        history = []  # Her neslin en iyi skorunu kaydet
        
        # Her nesil için evrim döngüsü
        for gen in range(1, self.generations + 1):
            # --- 1. SEÇİLİM (SELECTION) ---
            # Popülasyonu fitness skoruna göre sırala (yüksekten düşüğe)
            self.population.sort(key=lambda x: x[1], reverse=True)
            best_individual = self.population[0]  # En iyi birey
            display_score = max(0, best_individual[1])  # Negatif skorları 0'a çek
            
            # Geçmişe kaydet
            history.append({
                "generation": gen,
                "best_score": display_score,
                "best_code": best_individual[0]
            })
            
            # Hedef tutturuldu mu? (%100 coverage)
            if display_score >= 100:
                break  # Evrimi durdur
            
            # --- 2. ÜREME (REPRODUCTION) ---
            # En iyi 2 bireyi hayatta tut (survivors)
            survivors = self.population[:2]
            next_gen = []
            
            # Elitizm: En iyi bireyi yeni nesle direkt aktar (kaybetme)
            next_gen.append(survivors[0])
            
            # Yeni nesli oluştur (popülasyon büyüklüğüne ulaşana kadar)
            while len(next_gen) < self.population_size:
                time.sleep(1)  # API rate limit için bekleme
                
                parent1 = survivors[0][0]  # En iyi birey
                parent2 = random.choice(survivors)[0]  # Rastgele bir survivor
                
                # %40 ihtimalle çaprazlama, %60 ihtimalle mutasyon
                if random.random() < 0.4:
                    child_code = self.crossover(parent1, parent2)
                else:
                    child_code = self.mutate(parent1)
                
                # Yeni bireyi değerlendir ve popülasyona ekle
                next_gen.append(self.evaluate(child_code))
            
            # Yeni nesli eski nesille değiştir
            self.population = next_gen
            
        return (best_individual[0], display_score), history