from pathlib import Path
from .models import AppEntry
from .providers import apt, flatpak

APPLICATION_DIRS = (
    Path("/usr/share/applications"),
    Path.home() / ".local/share/applications",
)


def _desktop_value(lines: dict[str, str], key: str) -> str:
    """Prioriza português e usa o valor padrão como fallback."""
    for localized in (f"{key}[pt_BR]", f"{key}[pt]"):
        if lines.get(localized):
            return lines[localized]
    return lines.get(key, "")


def list_desktop_apps() -> list[AppEntry]:
    """Lê metadados .desktop sem executar comandos dos lançadores."""
    found: dict[str, AppEntry] = {}
    for directory in APPLICATION_DIRS:
        if not directory.is_dir():
            continue
        for path in directory.glob("*.desktop"):
            values: dict[str, str] = {}
            try:
                for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
                    if "=" not in line or line.startswith(("#", "[")):
                        continue
                    key, value = line.split("=", 1)
                    if key in {"Name", "Name[pt_BR]", "Name[pt]",
                               "Comment", "Comment[pt_BR]", "Comment[pt]",
                               "NoDisplay", "Icon", "Categories", "Type"}:
                        values[key] = value
            except OSError:
                continue

            if values.get("Type", "Application") != "Application":
                continue
            if values.get("NoDisplay", "").strip().lower() == "true":
                continue

            name = _desktop_value(values, "Name") or path.stem
            summary = _desktop_value(values, "Comment")
            found.setdefault(path.stem, AppEntry(
                app_id=path.stem,
                name=name,
                summary=summary,
                source="Aplicativo do sistema",
                installed=True,
                desktop_file=str(path),
                icon_name=values.get("Icon", "").strip(),
                categories=values.get("Categories", "").strip(),
            ))

    return sorted(found.values(), key=lambda item: item.name.casefold())


def list_installed() -> list[AppEntry]:
    """Une inventários APT/Flatpak; nem todo pacote é app gráfico."""
    entries = apt.list_installed() + flatpak.list_installed()
    return sorted(entries, key=lambda item: (item.name.casefold(), item.source))
