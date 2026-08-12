import pygame
import config
from button import Button
from game.states.classes.baseMenu import BaseMenu

class MainMenuState(BaseMenu):
    def __init__(self, state_manager):
        buttons = [
            Button(22, 145, "Join Lobby", 28),
            Button(22, 185, "Settings", 28),
            Button(25, 225, "Exit", 28)
        ]
        super().__init__(state_manager, buttons)
        self.title_font = pygame.font.Font("assets/RamadhanMubarok.otf", 44)
        self.text_font = pygame.font.Font("assets/determination.ttf", 11)

    def draw(self, screen: pygame.Surface):
        super().draw(screen)

        title = self.title_font.render(
            "Supa Fighta",
            True,
            (244, 186, 98)
        )
        screen.blit(title, (20, 38))

        hint = self.text_font.render(
            "UP/DOWN Navigate   ENTER Select   ESC Exit",
            True,
            (225, 214, 199)
        )
        screen.blit(hint, (18, config.WINDOW_HEIGHT - 20))

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
