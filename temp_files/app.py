class BankAccount:
    def __init__(self, owner, balance=0):
        self.owner = owner
        self.balance = balance
        self.is_active = True

    def deposit(self, amount):
        if not self.is_active:
            return "Hesap pasif"
            
        if amount <= 0:
            return "Hata: Yatırılacak tutar pozitif olmalı"
        
        self.balance += amount
        
        # 10.000 TL üzeri yatırımlarda 100 TL bonus (Bunu test etmeyeceğiz!)
        if amount >= 10000:
            self.balance += 100
            
        return "Para yatırıldı"

    def withdraw(self, amount):
        if not self.is_active:
            return "Hesap pasif"
            
        if amount > self.balance:
            return "Hata: Yetersiz bakiye"
            
        if amount <= 0:
            return "Hata: Çekilecek tutar pozitif olmalı"
            
        self.balance -= amount
        return "Para çekildi"

    def close_account(self):
        self.is_active = False
        return "Hesap kapatıldı"