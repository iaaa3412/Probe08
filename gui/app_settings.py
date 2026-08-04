import json
import os

SETTINGS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "app_settings.json")


def load_settings() -> dict:
    try:
        with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def save_settings(data: dict) -> None:
    with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def get_default_ata_folder(system: str) -> "str | None":
    return load_settings().get("default_ata_folder", {}).get(system)


def set_default_ata_folder(system: str, folder: str) -> None:
    data = load_settings()
    data.setdefault("default_ata_folder", {})[system] = folder
    save_settings(data)
