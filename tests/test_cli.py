import io
import json
import unittest
from contextlib import redirect_stderr, redirect_stdout

from aviation_disruption.cli import main


class CliTests(unittest.TestCase):
    def test_cli_returns_json(self):
        stdout = io.StringIO()
        with redirect_stdout(stdout):
            code = main([
                "--wind-kts", "30",
                "--visibility-km", "4",
                "--precip-mm-h", "3",
                "--delay-rate", "0.25",
                "--cancel-rate", "0.02",
            ])
        self.assertEqual(code, 0)
        payload = json.loads(stdout.getvalue())
        self.assertIn(payload["band"], {"LOW", "MEDIUM", "HIGH"})
        self.assertIn("score", payload)
        self.assertIn("drivers", payload)

    def test_cli_rejects_invalid_rate(self):
        stderr = io.StringIO()
        with redirect_stderr(stderr):
            code = main([
                "--wind-kts", "10",
                "--visibility-km", "10",
                "--precip-mm-h", "0",
                "--delay-rate", "2",
                "--cancel-rate", "0",
            ])
        self.assertEqual(code, 2)
        self.assertIn("between 0 and 1", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
