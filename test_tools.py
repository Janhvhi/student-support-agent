
import unittest
from tools import check_fee_status, check_scholarship_status


class TestStudentTools(unittest.TestCase):

    def test_fee_status_for_existing_student(self):
        result = check_fee_status("STU001")
        self.assertEqual(result.get("fee_status"), "Paid")

    def test_scholarship_status_for_existing_student(self):
        result = check_scholarship_status("STU002")
        self.assertEqual(result.get("scholarship_status"), "Under Review")

    def test_missing_student(self):
        result = check_fee_status("STU999")
        self.assertIn("error", result)


if __name__ == "__main__":
    unittest.main(verbosity=2)
