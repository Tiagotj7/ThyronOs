from pathlib import Path
from .models import AppEntry
from .providers import apt, flatpak

APPLICATION_DIRS = (
    Path("/usr/share/applications"),
    Path.home() / ".local/share/applications",
)

def list_desktop_apps() -> list[AppEntry]:
    """Lê arquivos .desktop sem executar os aplicativos."""
    found: dict[str, AppEntry] = {}
    for directory in APPLICATION_DIRS:
        if not directory.is_dir():
            continue
        for path in directory.glob("*.desktop"):
            values: dict[str, str] = {}
            try:
                for line in path.read_text(errors="replace").splitlines():
                    if line.startswith(("Name=", "Comment=", "NoDisplay=")):
                        key, value = line.split("=", 1)
                        values[key] = value
            except OSError:
                continue
            if values.get("NoDisplay", "").lower() == "true":
                continue
            name = values.get("Name", path.stem)
            found.setdefault(path.stem, AppEntry(
                app_id=path.stem, name=name,
                summary=values.get("Comment", ""),
                source="Aplicativo do sistema",
                installed=True, desktop_file=str(path),
            ))
    return sorted(found.values(), key=lambda item: item.name.casefold())

def list_installed() -> list[AppEntry]:
    """Une inventários APT/Flatpak; não afirma que todo pacote é app gráfico."""
    entries = apt.list_installed() + flatpak.list_installed()
    return sorted(entries, key=lambda item: (item.name.casefold(), item.source))
