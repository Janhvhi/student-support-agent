
import unittest
from unittest.mock import patch
from memory import save_preference, load_memory


class TestStudentMemory(unittest.TestCase):

    def test_save_preference(self):
        with patch("memory.MEMORY_FILE") as mock_file:
            mock_file.exists.return_value = False

            # Use a temporary file for this test.
            import tempfile
            from pathlib import Path

            with tempfile.TemporaryDirectory() as temp_dir:
                test_file = Path(temp_dir) / "memory.json"

                with patch("memory.MEMORY_FILE", test_file):
                    result = save_preference(
                        "I prefer simple explanations."
                    )

                    self.assertIn("saved", result.lower())
                    self.assertIn(
                        "I prefer simple explanations.",
                        load_memory()
                    )

    def test_reject_sensitive_preference(self):
        result = save_preference("My password is secret123")
        self.assertIn("not saved", result.lower())


if __name__ == "__main__":
    unittest.main(verbosity=2)
