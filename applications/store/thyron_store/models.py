from dataclasses import dataclass

@dataclass(frozen=True, slots=True)
class AppEntry:
    app_id: str
    name: str
    summary: str = ""
    version: str = ""
    source: str = "unknown"
    installed: bool = False
    desktop_file: str = ""
