import json
import os
from pathlib import Path

from .models import AppEntry

DATA_HOME = Path(
    os.environ.get("XDG_DATA_HOME", Path.home() / ".local/share")
)
FAVORITES_FILE = DATA_HOME / "thyron-store" / "favorites.json"


def favorite_key(entry: AppEntry) -> str:
    return f"{entry.source}:{entry.app_id}"


def load_favorites() -> dict[str, AppEntry]:
    if not FAVORITES_FILE.is_file():
        return {}

    try:
        data = json.loads(FAVORITES_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}

    favorites = {}

    if not isinstance(data, list):
        return {}

    for item in data:
        if not isinstance(item, dict):
            continue

        try:
            entry = AppEntry(
                app_id=str(item["app_id"]),
                name=str(item["name"]),
                summary=str(item.get("summary", "")),
                version=str(item.get("version", "")),
                source=str(item.get("source", "unknown")),
                installed=bool(item.get("installed", False)),
                desktop_file=str(item.get("desktop_file", "")),
                icon_name=str(item.get("icon_name", "")),
                categories=str(item.get("categories", "")),
            )
        except (KeyError, TypeError, ValueError):
            continue

        favorites[favorite_key(entry)] = entry

    return favorites


def save_favorites(favorites: dict[str, AppEntry]) -> None:
    FAVORITES_FILE.parent.mkdir(parents=True, exist_ok=True)

    data = [
        {
            "app_id": entry.app_id,
            "name": entry.name,
            "summary": entry.summary,
            "version": entry.version,
            "source": entry.source,
            "installed": entry.installed,
            "desktop_file": entry.desktop_file,
            "icon_name": entry.icon_name,
            "categories": entry.categories,
        }
        for entry in sorted(
            favorites.values(),
            key=lambda item: item.name.casefold(),
        )
    ]

    temporary = FAVORITES_FILE.with_suffix(".json.tmp")

    temporary.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    temporary.replace(FAVORITES_FILE)
