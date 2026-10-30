import unittest
from auth import authenticate
from tools import check_fee_status, check_scholarship_status
from memory import is_sensitive

class SecurityTests(unittest.TestCase):
    def test_demo_login(self):
        self.assertEqual(authenticate("STU001", "student123")["student_id"], "STU001")
        self.assertIsNone(authenticate("STU001", "wrong"))

    def test_own_record_allowed(self):
        self.assertEqual(check_fee_status("STU001", "STU001")["fee_status"], "Paid")

    def test_other_record_blocked(self):
        self.assertIn("Access denied", check_fee_status("STU002", "STU001")["error"])

    def test_otp_and_password_not_saved(self):
        self.assertTrue(is_sensitive("My OTP is 123456"))
        self.assertTrue(is_sensitive("My password is abc123"))

if __name__ == "__main__":
    unittest.main()
