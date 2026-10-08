import unittest
from importlib.metadata import version

import aviation_disruption


class VersionTests(unittest.TestCase):
    def test_runtime_version_matches_installed_metadata(self):
        self.assertEqual(
            aviation_disruption.__version__,
            version("aviation-disruption-intelligence"),
        )

    def test_release_version(self):
        self.assertEqual(aviation_disruption.__version__, "0.4.1")


if __name__ == "__main__":
    unittest.main()
