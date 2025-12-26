from game.states.mainMenu import MainMenuState
from game.states.gameplayState import GameplayState
from game.states.lobby import LobbyState

class GameState:
    def __init__(self):
        self.current_state = MainMenuState(self)
        # Initialize lobby first since we need it for player object
        self.states = {
            "main_menu": MainMenuState(self),
            "lobby": LobbyState(self)
        }
        self.current_state.enter()

    def change_state(self, new_state: str):
        print(f"Changed state to: {new_state}")
        if new_state == "gameplay":
            lobby_state = self.states["lobby"]
            self.states["gameplay"] = GameplayState(lobby_state.get_player(), self)
        
        if new_state in self.states:
            self.current_state.exit()
            self.current_state = self.states[new_state]
            self.current_state.enter()

    def update(self):
        self.current_state.update()
    def draw(self, screen):
        self.current_state.draw(screen)
    def handle_event(self, event):
        self.current_state.handle_event(event)