import unittest
import tempfile
from pathlib import Path
from unittest.mock import patch
from applications.store.thyron_store.models import AppEntry
from applications.store.thyron_store import catalog

class StoreModelTests(unittest.TestCase):
    def test_entry_is_immutable_and_has_source(self):
        item = AppEntry(app_id="org.example.App", name="Example", source="Flatpak")
        self.assertEqual(item.source, "Flatpak")
        self.assertFalse(item.installed)
        self.assertEqual(item.icon_name, "")
        self.assertEqual(item.categories, "")

    def test_desktop_catalog_reads_icon_and_categories(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            desktop_file = Path(temp_dir) / "example.desktop"
            desktop_file.write_text(
                "[Desktop Entry]\n"
                "Type=Application\n"
                "Name=Example\n"
                "Name[pt_BR]=Exemplo\n"
                "Comment=Example app\n"
                "Icon=example-icon\n"
                "Categories=Utility;\n",
                encoding="utf-8",
            )
            with patch.object(catalog, "APPLICATION_DIRS", (Path(temp_dir),)):
                entries = catalog.list_desktop_apps()

        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0].name, "Exemplo")
        self.assertEqual(entries[0].icon_name, "example-icon")
        self.assertEqual(entries[0].categories, "Utility;")

    def test_entry_accepts_desktop_metadata(self):
        item = AppEntry(
            app_id="org.example.App", name="Example",
            icon_name="example-icon", categories="Utility;",
        )
        self.assertEqual(item.icon_name, "example-icon")
        self.assertEqual(item.categories, "Utility;")

if __name__ == "__main__":
    unittest.main()
