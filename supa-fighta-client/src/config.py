# Game settings
WINDOW_WIDTH = 640
WINDOW_HEIGHT = 360
FPS = 60
PLAYER_SIZE = 50
PLAYER_COLOR = (0, 255, 0)
BACKGROUND_COLOR = (255, 255, 255)
DEBUG = True

# Sprites 
SPRITES = {
    "idle": {
        "path": "./supa-fighta-client/assets/Idel.png",
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
        "path": "./supa-fighta-client/assets/Walk.png",
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
        "path": "./supa-fighta-client/assets/Dash.png",
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
        "path": "./supa-fighta-client/assets/Punch.png",
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
        "path": "./supa-fighta-client/assets/Parry.png",
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
        "path": "./supa-fighta-client/assets/Wait.png",
        "rows": 1,
        "cols": 7,
        "width": 120,
        "height": 120,
        "hitbox": None,
        "hurtbox": (80,120),
        "frame_rate": 12,
        "loop": True,
    },
}

# WebSocket settings
WS_URL = "ws://localhost:8080"
PLAYER_ID = None