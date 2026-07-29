from game.states.mainMenu import MainMenuState
from game.states.gameplayState import GameplayState
from game.states.lobby import LobbyState
from game.states.settingsMenu import SettingsState
from game.states.nameMenu import NameMenuState
from game.states.connectionError import ConnectionErrorState
from animations.sprites import SpriteSheet
from animations.animation import Animator
from type.sprite import SpriteProperties
import config

class GameState:
    def __init__(
        self,
        game_display=None,
        on_display_resolution_changed=None,
    ):
        self.game_display = game_display
        self.on_display_resolution_changed = on_display_resolution_changed
        self._display_resolution = config.DEFAULT_DISPLAY_RESOLUTION
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
            "name_menu": NameMenuState(self),
            "connection_error": ConnectionErrorState(self)
        }
        self.change_state("main_menu")

    def change_state(self, new_state: str):
        if config.DEBUG:
            print(f"Changed state to: {new_state}")
        if self.state_stack:
            current_state = self.state_stack[-1]
            if hasattr(current_state, 'exit'):
                current_state.exit()
        if new_state == "gameplay":
            lobby_state = self.states["lobby"]
            player_name, opponent_name = lobby_state.get_match_player_names()
            self.states["gameplay"] = GameplayState(
                lobby_state.get_player(),
                self,
                lobby_state.get_match_countdown_seconds(),
                lobby_state.get_match_duration_seconds(),
                player_name,
                opponent_name
            )
        # reset stack so we don't have to worry about going back to old states with old data
        self.state_stack = []
        state = self.states.get(new_state)
        if state:
            self.state_stack.append(state)
            state.enter()

    def show_connection_error(self, message):
        lobby_state = self.states["lobby"]
        lobby_state.disconnect_player()
        error_state = self.states["connection_error"]
        error_state.set_message(message)

        if self.current_state() == error_state:
            return

        self.change_state("connection_error")

    def show_name_error(self, message):
        lobby_state = self.states["lobby"]
        lobby_state.disconnect_player()
        self.change_state("settings")
        self.push_state(NameMenuState(self, message))

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

    def get_display_resolution(self):
        if self.game_display is not None:
            return self.game_display.resolution
        return self._display_resolution

    def cycle_display_resolution(self, direction=1):
        current_index = config.DISPLAY_RESOLUTIONS.index(
            self.get_display_resolution()
        )
        next_index = (
            current_index + direction
        ) % len(config.DISPLAY_RESOLUTIONS)
        return self.set_display_resolution(
            config.DISPLAY_RESOLUTIONS[next_index]
        )

    def set_display_resolution(self, resolution):
        resolution = tuple(resolution)
        if resolution not in config.DISPLAY_RESOLUTIONS:
            raise ValueError(f"Unsupported display resolution: {resolution}")
        if self.game_display is not None:
            applied_resolution = self.game_display.set_resolution(resolution)
        else:
            self._display_resolution = resolution
            applied_resolution = self._display_resolution

        if self.on_display_resolution_changed is not None:
            self.on_display_resolution_changed(applied_resolution)
        return applied_resolution

    def draw_background(self, screen):
        self.background.draw(screen)

    def update_background(self):
        self.background.update()
