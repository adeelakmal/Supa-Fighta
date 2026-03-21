from game.states.mainMenu import MainMenuState
from game.states.gameplayState import GameplayState
from game.states.lobby import LobbyState
from game.states.settingsMenu import SettingsState
from game.states.nameMenu import NameMenuState
from animations.sprites import SpriteSheet
from animations.animation import Animator
from type.sprite import SpriteProperties
import config

class GameState:
    def __init__(self):
        self.state_stack = []
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
            "settings": SettingsState(self),
            "name_menu": NameMenuState(self)
        }
        self.change_state("main_menu")

    def change_state(self, new_state: str):
        if config.DEBUG:
            print(f"Changed state to: {new_state}")
        if new_state == "gameplay":
            lobby_state = self.states["lobby"]
            self.states["gameplay"] = GameplayState(lobby_state.get_player(), self)
        # reset stack so we don't have to worry about going back to old states with old data
        self.state_stack = []
        state = self.states.get(new_state)
        if state:
            self.state_stack.append(state)
            state.enter()

    def push_state(self, state):
        self.state_stack.append(state)

    def pop_state(self):
        if len(self.state_stack) > 1:
            self.state_stack.pop()

    def current_state(self):
        return self.state_stack[-1] if self.state_stack else None

    def update(self):
        for state in self.state_stack:
            state.update()

    def draw(self, screen):
        for state in self.state_stack:
            state.draw(screen)

    def handle_event(self, event):
        if self.state_stack:
            # only top gets input
            self.state_stack[-1].handle_event(event)

    def draw_background(self, screen):
        self.background.draw(screen)

    def update_background(self):
        self.background.update()