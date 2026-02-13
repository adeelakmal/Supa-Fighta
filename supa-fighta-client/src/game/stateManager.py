from game.states.mainMenu import MainMenuState
from game.states.gameplayState import GameplayState
from game.states.lobby import LobbyState

class GameState:
    def __init__(self):
        self.current_state = None
        # Initialize lobby first since we need it for player object
        self.states = {
            "main_menu": MainMenuState(self),
            "lobby": LobbyState(self)
        }
        self.change_state("main_menu")

    def change_state(self, new_state: str):
        print(f"Changed state to: {new_state}")
        if new_state == "gameplay":
            lobby_state = self.states["lobby"]
            self.states["gameplay"] = GameplayState(lobby_state.get_player(), self)
        
        if self.current_state:
            self.current_state.exit()
            self.current_state = None
        self.current_state = self.states.get(new_state)
        if self.current_state:
            self.current_state.enter()

    def update(self):
        if self.current_state:
            self.current_state.update()
            
    def draw(self, screen):
        if self.current_state:
            self.current_state.draw(screen)
            
    def handle_event(self, event):
        if self.current_state:
            self.current_state.handle_event(event)