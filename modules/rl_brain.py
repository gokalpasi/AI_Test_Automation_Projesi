import numpy as np
import os
import json

class QLearningBrain:
    def __init__(self, actions, learning_rate=0.1, reward_decay=0.9, e_greedy=0.9):
        self.actions = actions  # Yapılabilecek eylemler listesi
        self.lr = learning_rate
        self.gamma = reward_decay
        self.epsilon = e_greedy
        
        # Q-Tablosunu dosyadn yükle veya yeni oluştur
        self.q_table_file = "q_table.json"
        self.q_table = self.load_q_table()

    def load_q_table(self):
        if os.path.exists(self.q_table_file):
            try:
                with open(self.q_table_file, 'r') as f:
                    # JSON keyleri string'dir, onları tuple'a çevirmemiz gerekebilir ama
                    # basitlik için string "state" kullanacağız.
                    return json.load(f)
            except:
                return {}
        return {}

    def save_q_table(self):
        with open(self.q_table_file, 'w') as f:
            json.dump(self.q_table, f)

    def check_state_exist(self, state):
        if state not in self.q_table:
            # O durum için tüm aksiyonlara 0 değeri ata
            self.q_table[state] = {action: 0.0 for action in self.actions}

    def choose_action(self, state):
        self.check_state_exist(state)
        # Epsilon-Greedy Stratejisi
        # %90 ihtimalle en iyi bildiğini yap, %10 ihtimalle keşfet (rastgele)
        if np.random.uniform() < self.epsilon:
            state_actions = self.q_table[state]
            # En yüksek değere sahip aksiyonu seç
            # Eğer hepsi eşitse rastgele seç
            max_val = max(state_actions.values())
            best_actions = [k for k, v in state_actions.items() if v == max_val]
            action = np.random.choice(best_actions)
        else:
            # Rastgele keşfet
            action = np.random.choice(self.actions)
        return action

    def learn(self, state, action, reward, next_state):
        self.check_state_exist(next_state)
        
        # Q-Learning Formülü:
        # Q(s,a) = Q(s,a) + lr * [R + gamma * max(Q(s',a')) - Q(s,a)]
        
        q_predict = self.q_table[state][action]
        
        if next_state != 'DONE':
            q_target = reward + self.gamma * max(self.q_table[next_state].values())
        else:
            q_target = reward  # Son durum

        # Değeri güncelle
        self.q_table[state][action] += self.lr * (q_target - q_predict)
        
        # Diske kaydet (Hoca görsün diye)
        self.save_q_table()