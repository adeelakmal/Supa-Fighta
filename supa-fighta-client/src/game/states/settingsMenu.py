import pygame
import config
from button import Button
from game.states.classes.baseMenu import BaseMenu
from game.states.nameMenu import NameMenuState
from game.states.resolutionMenu import ResolutionMenuState


class SettingsState(BaseMenu):

    def __init__(self, state_manager):
        buttons = [
            Button(16, config.WINDOW_HEIGHT - 190, "Player Name", 30),
            Button(16, config.WINDOW_HEIGHT - 150, "Sound", 30),
            Button(16, config.WINDOW_HEIGHT - 110, "Resolution", 30)
        ]
        super().__init__(state_manager, buttons)
        self.hint_font = pygame.font.Font("assets/determination.ttf", 9)

    def draw(self, screen: pygame.Surface):
        sound_button = next(
            button
            for button in self.buttons
            if button.text.startswith("Sound")
        )
        sound_button.set_text(self.sound_loader.get_status_text())
        super().draw(screen)
        hint = self.hint_font.render(
            "ESC  Back",
            True,
            (225, 214, 199)
        )
        screen.blit(
            hint,
            (config.WINDOW_WIDTH - hint.get_width() - 16,
             config.WINDOW_HEIGHT - 16)
        )

    def handle_event(self, event):
        super().handle_event(event)

    def _activate(self, text):
        super()._activate(text)

        if text == "Player Name":
            self.state_manager.push_state(NameMenuState(self.state_manager))

        elif text.startswith("Sound"):
            self.sound_loader.toggle_mute()

        elif text == "Resolution":
            self.state_manager.push_state(
                ResolutionMenuState(self.state_manager)
            )

    def _on_escape(self):
        self._go_back()

    def _go_back(self):
        self.state_manager.change_state("main_menu")
