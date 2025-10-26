from player_manager import load_player_id

# Game settings
WINDOW_WIDTH = 640
WINDOW_HEIGHT = 360
FPS = 60
PLAYER_SIZE = 50
PLAYER_COLOR = (0, 255, 0)
BACKGROUND_COLOR = (255, 255, 255)

# WebSocket settings
WS_URL = "ws://localhost:8080"
PLAYER_ID = load_player_id()