import json
import os
import tempfile
from pathlib import Path

import config


APPLICATION_DIRECTORY = "Supa-Fighta"
SETTINGS_FILENAME = "settings.json"


def get_settings_path():
    """Return a per-user path that remains stable between game launches."""
    if os.name == "nt":
        base_directory = os.environ.get("LOCALAPPDATA")
        if base_directory:
            return (
                Path(base_directory)
                / APPLICATION_DIRECTORY
                / SETTINGS_FILENAME
            )

    base_directory = os.environ.get("XDG_CONFIG_HOME")
    if base_directory:
        return (
            Path(base_directory)
            / APPLICATION_DIRECTORY.lower()
            / SETTINGS_FILENAME
        )

    return (
        Path.home()
        / ".config"
        / APPLICATION_DIRECTORY.lower()
        / SETTINGS_FILENAME
    )


def _validated_resolution(value):
    if not isinstance(value, (list, tuple)) or len(value) != 2:
        return None
    if any(type(dimension) is not int for dimension in value):
        return None

    resolution = tuple(value)
    if resolution not in config.DISPLAY_RESOLUTIONS:
        return None
    return resolution


def load_display_resolution(path=None):
    """Load a saved preset, falling back safely for absent or invalid data."""
    settings_path = Path(path) if path is not None else get_settings_path()
    try:
        with settings_path.open("r", encoding="utf-8") as settings_file:
            settings = json.load(settings_file)
    except (OSError, json.JSONDecodeError, TypeError):
        return config.DEFAULT_DISPLAY_RESOLUTION

    if not isinstance(settings, dict):
        return config.DEFAULT_DISPLAY_RESOLUTION

    return (
        _validated_resolution(settings.get("display_resolution"))
        or config.DEFAULT_DISPLAY_RESOLUTION
    )


def save_display_resolution(resolution, path=None):
    """Atomically save a supported display preset without interrupting play."""
    resolution = _validated_resolution(resolution)
    if resolution is None:
        raise ValueError("Unsupported display resolution")

    settings_path = Path(path) if path is not None else get_settings_path()
    temporary_path = None
    try:
        settings_path.parent.mkdir(parents=True, exist_ok=True)

        settings = {}
        try:
            with settings_path.open("r", encoding="utf-8") as settings_file:
                loaded_settings = json.load(settings_file)
            if isinstance(loaded_settings, dict):
                settings.update(loaded_settings)
        except (OSError, json.JSONDecodeError, TypeError):
            pass

        settings["display_resolution"] = list(resolution)
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=settings_path.parent,
            prefix=f".{settings_path.name}.",
            suffix=".tmp",
            delete=False,
        ) as temporary_file:
            temporary_path = Path(temporary_file.name)
            json.dump(settings, temporary_file, indent=2)
            temporary_file.write("\n")

        os.replace(temporary_path, settings_path)
        return True
    except OSError as error:
        print(f"Could not save display resolution: {error}")
        return False
    finally:
        if temporary_path is not None and temporary_path.exists():
            try:
                temporary_path.unlink()
            except OSError:
                pass
