import shutil
import subprocess
from ..models import AppEntry

def list_installed() -> list[AppEntry]:
    """Inventário dpkg somente leitura; não executa operações administrativas."""
    if not shutil.which("dpkg-query"):
        return []
    result = subprocess.run(
        ["dpkg-query", "-W", "-f=${binary:Package}\t${Version}\n"],
        check=False, capture_output=True, text=True, timeout=20,
    )
    if result.returncode != 0:
        return []
    entries = []
    for line in result.stdout.splitlines():
        parts = line.split("\t", 1)
        if len(parts) == 2 and parts[0]:
            entries.append(AppEntry(
                app_id=parts[0], name=parts[0], version=parts[1],
                source="APT/dpkg", installed=True,
            ))
    return entries
