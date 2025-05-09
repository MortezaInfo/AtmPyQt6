import unittest
import redis
from atm_app import ATM

class TestATM(unittest.TestCase):
    def setUp(self):
        self.r = redis.Redis(host='localhost', port=6379, decode_responses=True)
        self.r.flushdb()
        self.atm = ATM()

    def test_initial_balance(self):
        self.assertEqual(self.atm.get_balance(), 1000000)

    def test_withdraw_success(self):
        result = self.atm.withdraw(500000)
        self.assertTrue(result)
        self.assertEqual(self.atm.get_balance(), 500000)

    def test_withdraw_fail(self):
        result = self.atm.withdraw(2000000)
        self.assertFalse(result)

    def test_change_password(self):
        self.atm.change_password("4321")
        self.assertEqual(self.atm.password, "4321")

    def test_transfer(self):
        result = self.atm.transfer(200000)
        self.assertTrue(result)
        self.assertEqual(self.atm.get_balance(), 800000)

if __name__ == '__main__':
    unittest.main()
