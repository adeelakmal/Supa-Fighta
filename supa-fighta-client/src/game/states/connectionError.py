import pygame

import config
from button import Button
from game.states.classes.baseMenu import BaseMenu


class ConnectionErrorState(BaseMenu):
    def __init__(self, state_manager):
        buttons = [
            Button(0, config.WINDOW_HEIGHT - 125, "Retry"),
            Button(0, config.WINDOW_HEIGHT - 85, "Main Menu"),
        ]

        # Center the text and make the whole label clickable.
        for button in buttons:
            text_width = button.font.size(button.text)[0]
            button.rect.x = (config.WINDOW_WIDTH - text_width) // 2
            button.rect.width = text_width

        super().__init__(state_manager, buttons)
        self.message = "The connection to the server was lost."
        self.title_font = pygame.font.SysFont(None, 54, bold=True)
        self.message_font = pygame.font.SysFont(None, 25)

    def set_message(self, message):
        self.message = message

    def draw(self, screen):
        self.state_manager.draw_background(screen)

        overlay = pygame.Surface(
            (config.WINDOW_WIDTH, config.WINDOW_HEIGHT),
            pygame.SRCALPHA
        )
        overlay.fill((0, 0, 0, 165))
        screen.blit(overlay, (0, 0))

        title = self.title_font.render("CONNECTION LOST", True, (245, 80, 80))
        title_rect = title.get_rect(
            center=(config.WINDOW_WIDTH // 2, config.WINDOW_HEIGHT // 3)
        )
        screen.blit(title, title_rect)

        message = self.message_font.render(self.message, True, (245, 245, 245))
        message_rect = message.get_rect(
            center=(config.WINDOW_WIDTH // 2, config.WINDOW_HEIGHT // 2)
        )
        screen.blit(message, message_rect)

        # Draw these last so they stay bright on top of the dark overlay.
        for button in self.buttons:
            button.draw(screen)

    def _activate(self, text):
        super()._activate(text)
        if text == "Retry":
            self.state_manager.change_state("lobby")
        elif text == "Main Menu":
            self.state_manager.change_state("main_menu")

    def _on_escape(self):
        self.state_manager.change_state("main_menu")
