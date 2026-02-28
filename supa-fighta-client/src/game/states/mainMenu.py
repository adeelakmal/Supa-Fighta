import pygame
import config
from button import Button
from game.states.classes.baseMenu import BaseMenu

class MainMenuState(BaseMenu):
    def __init__(self, state_manager):
        buttons = [
            Button(22, config.WINDOW_HEIGHT - 190, "Join Lobby"),
            Button(22, config.WINDOW_HEIGHT - 150, "Settings"),
            Button(25, config.WINDOW_HEIGHT - 110, "Exit")
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