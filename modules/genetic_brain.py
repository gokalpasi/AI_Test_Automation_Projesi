import random
import time
from modules.ai_generator import generate_test_code_from_gemini
from modules.coverage_tool import run_coverage_analysis

class GeneticOptimizer:
    def __init__(self, source_code, initial_test_code, population_size=4, generations=3):
        self.source_code = source_code
        self.initial_test_code = initial_test_code
        self.population_size = population_size
        self.generations = generations
        self.population = [] 
        
        # --- YENİ EKLENDİ: SAYAÇ ---
        self.total_tests_run = 0 

    def initialize_population(self):
        """Başlangıç popülasyonunu oluşturur."""
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
            
        self.population.append(self.evaluate(base_code))
        
        for _ in range(self.population_size - 1):
            time.sleep(1) 
            mutated = self.mutate(base_code)
            self.population.append(self.evaluate(mutated))

    def evaluate(self, test_code):
        """Fitness Fonksiyonu: Coverage oranını ölçer."""
        
        # --- YENİ EKLENDİ: HER TESTTE SAYACI ARTIR ---
        self.total_tests_run += 1
        
        try:
            result, _ = run_coverage_analysis(self.source_code, test_code)
            score = result.get('coverage_percent', 0)
            
            if not result.get('success', False):
                score = -100 
                
            return (test_code, score)
        except Exception:
            return (test_code, -100)

    def mutate(self, test_code):
        """Genetik Mutasyon Operatörü"""
        mutation_type = random.choice([
            "VALUE_MODIFICATION", 
            "ADD_NEW_ASSERT",     
            "REMOVE_LINE",        
            "LOGIC_FLIP"          
        ])
        
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
        """Çaprazlama: İki kodun özelliklerini karıştır."""
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
        """Ana Evrim Döngüsü."""
        self.initialize_population()
        history = []
        
        for gen in range(1, self.generations + 1):
            # 1. Selection
            self.population.sort(key=lambda x: x[1], reverse=True)
            best_individual = self.population[0]
            display_score = max(0, best_individual[1])
            
            history.append({
                "generation": gen,
                "best_score": display_score,
                "best_code": best_individual[0]
            })
            
            if display_score >= 100:
                break
            
            # 2. Reproduction
            survivors = self.population[:2]
            next_gen = []
            next_gen.append(survivors[0]) # Elitizm
            
            while len(next_gen) < self.population_size:
                time.sleep(1) 
                parent1 = survivors[0][0]
                parent2 = random.choice(survivors)[0]
                
                if random.random() < 0.4:
                    child_code = self.crossover(parent1, parent2)
                else:
                    child_code = self.mutate(parent1)
                
                next_gen.append(self.evaluate(child_code))
            
            self.population = next_gen
            
        return (best_individual[0], display_score), history