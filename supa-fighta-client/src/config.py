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
    "hurt": {
        "path": "./supa-fighta-client/assets/Hurt.png",
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
        "path": "./supa-fighta-client/assets/Win.png",
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
        "path": "./supa-fighta-client/assets/Parry-Hit.png",
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
        "path": "./supa-fighta-client/assets/Parried.png",
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
        "path": "./supa-fighta-client/assets/punch.wav"
    },
    "dash" : {
        "path": "./supa-fighta-client/assets/dash.wav"
    },
    "parry" : {
        "path": "./supa-fighta-client/assets/parry.wav"
    },
    "button_hover" : {
        "path": "./supa-fighta-client/assets/button_hover.wav",
        "min_repeat_gap_ms": 50
    },
    "button_select" : {
        "path": "./supa-fighta-client/assets/button_select.wav",
        "min_repeat_gap_ms": 250
    }
}

# BACKGROUND MUSIC
MUSIC = {
    "menu" : "./supa-fighta-client/assets/menu_music.wav",
    "fight" : "./supa-fighta-client/assets/fight_music.wav"
}

# WebSocket settings
WS_URL = "ws://localhost:8080"
PLAYER_ID = None