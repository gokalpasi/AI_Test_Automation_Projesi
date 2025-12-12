from app import *
import unittest

class TestBankAccount(unittest.TestCase):
    def setUp(self):
        # Her testten önce çalışır
        self.account = BankAccount("Ahmet", 1000)

    def test_deposit_normal(self):
        # Normal para yatırma testi
        sonuc = self.account.deposit(500)
        self.assertEqual(sonuc, "Para yatırıldı")
        self.assertEqual(self.account.balance, 1500)

    def test_withdraw_normal(self):
        # Normal para çekme testi
        sonuc = self.account.withdraw(200)
        self.assertEqual(sonuc, "Para çekildi")
        self.assertEqual(self.account.balance, 800)
        
    def test_close_account(self):
        # Hesap kapatma testi
        sonuc = self.account.close_account()
        self.assertFalse(self.account.is_active)