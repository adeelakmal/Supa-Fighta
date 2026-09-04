import json
import os
import re
import uuid
from pathlib import Path


PLAYER_TOKEN_PATTERN = re.compile(r"^[A-Za-z0-9_-]{43}$")


def _valid_player_id(player_id):
    if not isinstance(player_id, str):
        return False

    try:
        parsed = uuid.UUID(player_id)
    except (ValueError, AttributeError):
        return False

    return parsed.version == 4 and str(parsed) == player_id.lower()


def _valid_player_token(player_token):
    return (
        isinstance(player_token, str)
        and PLAYER_TOKEN_PATTERN.fullmatch(player_token) is not None
    )


def load_player_credentials(credentials_file):
    path = Path(credentials_file)
    try:
        with path.open("r", encoding="utf-8") as file:
            credentials = json.load(file)
    except (OSError, UnicodeError, json.JSONDecodeError):
        return None

    if not isinstance(credentials, dict):
        return None

    player_id = credentials.get("playerId")
    player_token = credentials.get("playerToken")
    if not _valid_player_id(player_id) or not _valid_player_token(player_token):
        return None

    return {
        "playerId": player_id.lower(),
        "playerToken": player_token,
    }


def save_player_credentials(player_id, player_token, credentials_file="player_credentials.json"):
    if not _valid_player_id(player_id) or not _valid_player_token(player_token):
        return False

    path = Path(credentials_file)
    temporary_path = path.with_name(f"{path.name}.tmp")
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with temporary_path.open("w", encoding="utf-8") as file:
            json.dump(
                {"playerId": player_id.lower(), "playerToken": player_token},
                file,
                separators=(",", ":"),
            )
        os.replace(temporary_path, path)
    except OSError:
        try:
            temporary_path.unlink(missing_ok=True)
        except OSError:
            pass
        return False

    return True


def clear_player_credentials(credentials_file="player_credentials.json"):
    try:
        Path(credentials_file).unlink(missing_ok=True)
    except OSError:
        return False
    return True
