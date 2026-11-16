import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from applications.store.thyron_store import ui


class StoreSettingsTests(unittest.TestCase):
    def test_default_settings_are_safe(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch.object(ui, "SETTINGS_FILE", Path(temp_dir) / "settings.json"):
                self.assertEqual(ui.load_settings(), {"show_read_only_notice": True})

    def test_settings_are_persisted_and_reloaded(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            settings_file = Path(temp_dir) / "settings.json"
            with patch.object(ui, "SETTINGS_FILE", settings_file):
                expected = {"show_read_only_notice": False}
                ui.save_settings(expected)
                self.assertEqual(ui.load_settings(), expected)


if __name__ == "__main__":
    unittest.main()
