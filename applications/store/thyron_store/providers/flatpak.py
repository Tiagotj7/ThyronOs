import shutil
import subprocess
from ..models import AppEntry

def list_installed() -> list[AppEntry]:
    """Inventário Flatpak somente leitura; retorna vazio se indisponível."""
    if not shutil.which("flatpak"):
        return []
    result = subprocess.run(
        ["flatpak", "list", "--app", "--columns=application,name,version"],
        check=False, capture_output=True, text=True, timeout=20,
    )
    if result.returncode != 0:
        return []
    entries = []
    for line in result.stdout.splitlines():
        parts = line.split("\t")
        if parts and parts[0]:
            app_id = parts[0]
            name = parts[1] if len(parts) > 1 and parts[1] else app_id
            version = parts[2] if len(parts) > 2 else ""
            entries.append(AppEntry(
                app_id=app_id, name=name, version=version,
                source="Flatpak", installed=True,
            ))
    return entries
