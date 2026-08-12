import pygame
from button import Button
from game.states.classes.baseMenu import BaseMenu

class MainMenuState(BaseMenu):
    def __init__(self, state_manager):
        buttons = [
            Button(22, 165, "Join Lobby", 28),
            Button(22, 205, "Settings", 28),
            Button(25, 245, "Exit", 28)
        ]
        super().__init__(state_manager, buttons)

    def _activate(self, text):
        super()._activate(text)
        if text == "Join Lobby":
            self.state_manager.change_state("lobby")
        elif text == "Settings":
            self.state_manager.change_state("settings")
        elif text == "Exit":
            pygame.event.post(pygame.event.Event(pygame.QUIT))

    def _on_escape(self):
        pygame.event.post(pygame.event.Event(pygame.QUIT))
