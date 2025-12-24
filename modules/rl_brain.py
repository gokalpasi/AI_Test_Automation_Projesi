"""
Q-Learning Beyin Modülü
Bu modül, Reinforcement Learning (Pekiştirmeli Öğrenme) algoritması olan
Q-Learning'i kullanarak ajanın en iyi stratejiyi öğrenmesini sağlar.

Q-Learning, bir durum (state) ve eylem (action) çifti için beklenen
gelecek ödülü (Q-değeri) öğrenir ve bu bilgiyi Q-tablosunda saklar.
"""

import numpy as np
import os
import json

class QLearningBrain:
    """
    Q-Learning algoritmasını uygulayan sınıf.
    
    Bu sınıf, ajanın farklı durumlarda hangi eylemleri seçmesi gerektiğini
    öğrenmesini sağlar. Q-tablosu, durum-eylem çiftlerinin beklenen değerlerini
    saklar ve epsilon-greedy stratejisi ile keşif-yararlanma dengesini kurar.
    """
    
    def __init__(self, actions, learning_rate=0.1, reward_decay=0.9, e_greedy=0.9):
        """
        Q-Learning beyin yapılandırması.
        
        Args:
            actions: Yapılabilecek eylemlerin listesi (örn: ["STRATEJI_STANDART", ...])
            learning_rate: Öğrenme hızı (0.1 = %10, ne kadar hızlı öğreneceği)
            reward_decay: Ödül çürüme faktörü (0.9 = gelecek ödülleri %90 ağırlıkla dikkate al)
            e_greedy: Epsilon-greedy parametresi (0.9 = %90 ihtimalle en iyi eylemi seç, %10 keşfet)
        """
        self.actions = actions  # Yapılabilecek eylemler listesi
        self.lr = learning_rate  # Öğrenme hızı (alpha)
        self.gamma = reward_decay  # Gelecek ödül indirim faktörü (discount factor)
        self.epsilon = e_greedy  # Keşif-istismar dengesi parametresi
        
        # Q-Tablosunu dosyadan yükle veya yeni oluştur
        # Q-tablosu: {state: {action: Q_value}} formatında sözlük
        self.q_table_file = "q_table.json"
        self.q_table = self.load_q_table()

    def load_q_table(self):
        """
        Kaydedilmiş Q-tablosunu diskten yükler.
        
        Returns:
            dict: Q-tablosu sözlüğü. Eğer dosya yoksa veya hata varsa boş sözlük döner.
        """
        if os.path.exists(self.q_table_file):
            try:
                with open(self.q_table_file, 'r') as f:
                    # JSON keyleri string'dir, onları tuple'a çevirmemiz gerekebilir ama
                    # basitlik için string "state" kullanacağız.
                    return json.load(f)
            except Exception:
                # Dosya bozuk veya okunamazsa boş tablo döndür
                return {}
        return {}

    def save_q_table(self):
        """
        Q-tablosunu diske kaydeder.
        
        Bu sayede öğrenilen bilgiler kalıcı olur ve program yeniden başlatıldığında
        önceki deneyimler korunur.
        """
        with open(self.q_table_file, 'w') as f:
            json.dump(self.q_table, f, indent=2)

    def check_state_exist(self, state):
        """
        Verilen durumun Q-tablosunda olup olmadığını kontrol eder.
        Yoksa, o durum için tüm eylemlere 0 değeri atar.
        
        Args:
            state: Kontrol edilecek durum (string)
        """
        if state not in self.q_table:
            # Yeni durum: O durum için tüm aksiyonlara başlangıç değeri (0.0) ata
            self.q_table[state] = {action: 0.0 for action in self.actions}

    def choose_action(self, state):
        """
        Epsilon-greedy stratejisi ile eylem seçer.
        
        Bu strateji, keşif (exploration) ve istismar (exploitation) arasında
        denge kurar:
        - Epsilon olasılığıyla: En iyi bilinen eylemi seç (istismar)
        - (1-epsilon) olasılığıyla: Rastgele eylem seç (keşif)
        
        Args:
            state: Mevcut durum
            
        Returns:
            str: Seçilen eylem
        """
        # Durumun tabloda olduğundan emin ol
        self.check_state_exist(state)
        
        # Epsilon-Greedy Stratejisi
        # Epsilon (örn: 0.9) ihtimalle en iyi bildiğini yap, (1-epsilon) ihtimalle keşfet
        if np.random.uniform() < self.epsilon:
            # İSTİSMAR: En yüksek Q-değerine sahip eylemi seç
            state_actions = self.q_table[state]
            # En yüksek değere sahip eylemi bul
            max_val = max(state_actions.values())
            # Eğer birden fazla eylem aynı maksimum değere sahipse, rastgele birini seç
            best_actions = [k for k, v in state_actions.items() if v == max_val]
            action = np.random.choice(best_actions)
        else:
            # KEŞİF: Rastgele bir eylem seç (yeni stratejiler denemek için)
            action = np.random.choice(self.actions)
        return action

    def learn(self, state, action, reward, next_state):
        """
        Q-Learning algoritması ile öğrenme gerçekleştirir.
        
        Q-Learning formülü:
        Q(s,a) = Q(s,a) + lr * [R + gamma * max(Q(s',a')) - Q(s,a)]
        
        Bu formül, mevcut Q-değerini gerçek ödül ve gelecek tahmini ile günceller.
        
        Args:
            state: Mevcut durum
            action: Seçilen eylem
            reward: Alınan ödül (pozitif veya negatif)
            next_state: Bir sonraki durum
        """
        # Sonraki durumun tabloda olduğundan emin ol
        self.check_state_exist(next_state)
        
        # Q-Learning Formülü:
        # Q(s,a) = Q(s,a) + lr * [R + gamma * max(Q(s',a')) - Q(s,a)]
        # Burada:
        # - Q(s,a): Mevcut durum-eylem çiftinin değeri
        # - R: Alınan ödül
        # - gamma: Gelecek ödüllerin indirim faktörü
        # - max(Q(s',a')): Sonraki durumda mümkün olan en iyi eylemin değeri
        
        # Mevcut Q-değerini al (tahmin)
        q_predict = self.q_table[state][action]
        
        # Hedef Q-değerini hesapla
        if next_state != 'DONE':
            # Normal durum: Ödül + gelecek ödülün maksimum değeri
            q_target = reward + self.gamma * max(self.q_table[next_state].values())
        else:
            # Son durum: Sadece ödül (gelecek yok)
            q_target = reward

        # Q-değerini güncelle: Eski değer + öğrenme_hızı * (hedef - tahmin)
        # Bu, temporal difference learning (zaman farkı öğrenmesi) prensibidir
        self.q_table[state][action] += self.lr * (q_target - q_predict)
        
        # Öğrenilen bilgiyi diske kaydet (kalıcılık için)
        self.save_q_table()