from game.states.mainMenu import MainMenuState
from game.states.gameplayState import GameplayState
from game.states.lobby import LobbyState
from game.states.settingsMenu import SettingsState
from animations.sprites import SpriteSheet
from animations.animation import Animator
from type.sprite import SpriteProperties
import config

class GameState:
    def __init__(self):
        self.current_state = None
        self.previous_state = None
        self.background_sprites = SpriteSheet(
            SpriteProperties(
                path="assets/background.png",
                width=config.WINDOW_WIDTH,
                height=config.WINDOW_HEIGHT,
                rows=1,
                cols=8,
            )
        )
        self.background = Animator(self.background_sprites, 6)
        # Initialize lobby first since we need it for player object
        self.states = {
            "main_menu": MainMenuState(self),
            "lobby": LobbyState(self),
            "settings": SettingsState(self)
        }
        self.change_state("main_menu")

    def change_state(self, new_state: str):
        print(f"Changed state to: {new_state}")
        if new_state == "gameplay":
            lobby_state = self.states["lobby"]
            self.states["gameplay"] = GameplayState(lobby_state.get_player(), self)
        
        if self.current_state:
            self.previous_state = self.current_state
            self.current_state.exit()
            self.current_state = None
        self.current_state = self.states.get(new_state)
        if self.current_state:
            self.current_state.enter()

    def go_back(self):
        if self.previous_state:
            # Find the state name by comparing objects
            for state_name, state_obj in self.states.items():
                if state_obj is self.previous_state:
                    self.change_state(state_name)
                    break

    def update(self):
        if self.current_state:
            self.current_state.update()
            
    def draw(self, screen):
        if self.current_state:
            self.current_state.draw(screen)
            
    def handle_event(self, event):
        if self.current_state:
            self.current_state.handle_event(event)