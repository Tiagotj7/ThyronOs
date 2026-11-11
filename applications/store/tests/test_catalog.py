import unittest
from applications.store.thyron_store.models import AppEntry

class StoreModelTests(unittest.TestCase):
    def test_entry_is_immutable_and_has_source(self):
        item = AppEntry(app_id="org.example.App", name="Example", source="Flatpak")
        self.assertEqual(item.source, "Flatpak")
        self.assertFalse(item.installed)

if __name__ == "__main__":
    unittest.main()
