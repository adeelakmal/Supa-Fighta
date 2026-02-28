import pygame
import config
from button import Button
from game.states.classes.baseMenu import BaseMenu

class SettingsState(BaseMenu):
    def __init__(self, state_manager):
        buttons = [
            Button(15, config.WINDOW_HEIGHT - 190, "Player Name", 30),
            Button(15, config.WINDOW_HEIGHT - 150, "Sound", 30),
            Button(15, config.WINDOW_HEIGHT - 110, "Back", 30)
        ]
        super().__init__(state_manager, buttons)

    def draw(self, screen: pygame.Surface):
        super().draw(screen)

    def _activate(self, text):
        super()._activate(text)
        if text == "Player Name":
            # TODO: Implement player name settings
            pass
        elif text == "Sound":
            # TODO: Implement sound settings
            pass
        elif text == "Back":
            self._go_back()

    def _on_escape(self):
        self._go_back()

    def _go_back(self):
        self.state_manager.go_back()
