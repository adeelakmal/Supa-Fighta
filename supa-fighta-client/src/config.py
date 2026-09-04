import os

# Game settings
# Gameplay, collisions, networking, and assets use this fixed logical canvas.
# GameDisplay scales only the completed frame to a physical window size.
WINDOW_WIDTH = 640
WINDOW_HEIGHT = 360
LOGICAL_SIZE = (WINDOW_WIDTH, WINDOW_HEIGHT)
DISPLAY_RESOLUTIONS = (
    (640, 360),
    (1280, 720),
    (1920, 1080),
)
DEFAULT_DISPLAY_RESOLUTION = DISPLAY_RESOLUTIONS[0]
FPS = 60
PLAYER_MOVE_SPEED = 3.0
PLAYER_ACCELERATION = 0.45
PLAYER_DECELERATION = 0.65
PLAYER_SIZE = 50
PLAYER_COLOR = (0, 255, 0)
PLAYER_WIDTH = 80
BACKGROUND_COLOR = (255, 255, 255)
DEBUG = False

# Sprites 
SPRITES = {
    "idle": {
        "path": "assets/Idel.png",
        "rows": 1,
        "cols": 5,
        "width": 120,
        "height": 120,
        "hitbox": None,
        "hurtbox": (80,120),
        "frame_rate": 15,
        "loop": True,
    },
    "walk": {
        "path": "assets/Walk.png",
        "rows": 1,
        "cols": 5,
        "width": 120,
        "height": 120,
        "hitbox": None,
        "hurtbox": (80,120),
        "frame_rate": 15,
        "loop": True,
    },
    "dash": {
        "path": "assets/Dash.png",
        "rows": 1,
        "cols": 5,
        "width": 120,
        "height": 120,
        "hitbox": None,
        "hurtbox": (80,120),
        "frame_rate": 20,
        "loop": False,
    },
    "punch": {
        "path": "assets/Punch.png",
        "rows": 1,
        "cols": 9,
        "width": 120,
        "height": 120,
        "hitbox": (80,40,30,20), # x_offset(player_width), y_offset, width, height
        "hurtbox": (80,120),
        "frame_rate": 25,
        "loop": False,
    },
    "parry": {
        "path": "assets/Parry.png",
        "rows": 1,
        "cols": 5,
        "width": 120,
        "height": 120,
        "hitbox": None,
        "hurtbox": (80,120),
        "frame_rate": 15,
        "loop": False,
    },
    "wait": {
        "path": "assets/Wait.png",
        "rows": 1,
        "cols": 7,
        "width": 120,
        "height": 120,
        "hitbox": None,
        "hurtbox": (80,120),
        "frame_rate": 12,
        "loop": True,
    },
    "hurt": {
        "path": "assets/Hurt.png",
        "rows": 1,
        "cols": 8,
        "width": 120,
        "height": 120,
        "hitbox": None,
        "hurtbox": (80,120),
        "frame_rate": 10,
        "loop": False,
    },
    "win": {
        "path": "assets/Win.png",
        "rows": 1,
        "cols": 9,
        "width": 120,
        "height": 120,
        "hitbox": None,
        "hurtbox": (80,120),
        "frame_rate": 10,
        "loop": False,
    },
    "parry-hit": {
        "path": "assets/Parry-Hit.png",
        "rows": 1,
        "cols": 4,
        "width": 120,
        "height": 120,
        "hitbox": None,
        "hurtbox": (80,120),
        "frame_rate": 8,
        "loop": False,
    },
        "parried": {
        "path": "assets/Parried.png",
        "rows": 1,
        "cols": 4,
        "width": 120,
        "height": 120,
        "hitbox": None,
        "hurtbox": (80,120),
        "frame_rate": 10,
        "loop": False,
    },
}

#Recovery durations (in milliseconds)
RECOVERY_DURATIONS = {
    'punch': 500,
    'parry': 450
}

# SOUND EFFECTS
SOUND = {
    "punch" : {
        "path": "assets/punch.wav"
    },
    "dash" : {
        "path": "assets/dash.wav"
    },
    "parry" : {
        "path": "assets/parry.wav"
    },
    "button_hover" : {
        "path": "assets/button_hover.wav",
        "min_repeat_gap_ms": 50
    },
    "button_select" : {
        "path": "assets/button_select.wav",
        "min_repeat_gap_ms": 250
    }
}

# BACKGROUND MUSIC
MUSIC = {
    "menu" : "assets/menu_music.wav", 
    "fight" : "assets/fight_music.wav"
}

# WebSocket settings
WS_URL = os.getenv(
    "SUPA_FIGHTA_WS_URL",
    "wss://supa-fighta.onrender.com",
)
WS_CONNECT_TIMEOUT = 30
WS_HEARTBEAT_INTERVAL = 15
WS_HEARTBEAT_TIMEOUT = 45
PLAYER_ID = None
PLAYER_TOKEN = None
PLAYER_DATA_FILE = "player_credentials.json"
PLAYER_NAME = "Guest"
PLAYER_NAME_WAS_EDITED = False
