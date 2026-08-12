import re

MIN_PLAYER_NAME_LENGTH = 3
MAX_PLAYER_NAME_LENGTH = 20
ALLOWED_PLAYER_NAME = re.compile(r"^[A-Za-z0-9 _-]+$")
RESERVED_PLAYER_NAMES = {
    "admin",
    "developer",
    "guest",
    "moderator",
    "server",
    "system",
}


def validate_player_name(username):
    if not isinstance(username, str):
        return None, "Enter a player name."

    name = " ".join(username.split())

    if not MIN_PLAYER_NAME_LENGTH <= len(name) <= MAX_PLAYER_NAME_LENGTH:
        return None, "Name must be 3-20 characters."

    if not ALLOWED_PLAYER_NAME.fullmatch(name):
        return None, "Use only letters, numbers, spaces, _ or -."

    if name.casefold() in RESERVED_PLAYER_NAMES:
        return None, "That name is reserved."

    return name, None


def get_match_display_names(player_name, opponent_name):
    """Return clear in-match labels without changing either saved name."""
    opponent_display_name = opponent_name
    if (
        isinstance(player_name, str)
        and isinstance(opponent_name, str)
        and player_name.casefold() == opponent_name.casefold()
    ):
        opponent_display_name = f"{opponent_name} (2)"

    return "You", opponent_display_name
