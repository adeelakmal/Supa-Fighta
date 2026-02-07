# Game settings
WINDOW_WIDTH = 640
WINDOW_HEIGHT = 360
FPS = 60
PLAYER_SIZE = 50
PLAYER_COLOR = (0, 255, 0)
PLAYER_WIDTH = 80
BACKGROUND_COLOR = (255, 255, 255)
DEBUG = True

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
WS_URL = "ws://localhost:8080"
PLAYER_ID = None