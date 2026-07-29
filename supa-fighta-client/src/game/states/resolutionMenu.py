import pygame

import config
from button import Button
from game.states.classes.baseMenu import BaseMenu


class ResolutionMenuState(BaseMenu):
    PRESETS = config.DISPLAY_RESOLUTIONS
    PRESET_FONT_SIZE = 16
    PRESET_SPACING = 24
    PRESET_BUTTON_SIZE = (240, 24)
    TITLE_FONT_SIZE = 40
    TITLE_CENTER_Y_OFFSET = 36

    def __init__(self, state_manager):
        self.sub_menu_bg = pygame.image.load(
            "assets/sub_menu.png"
        ).convert_alpha()
        self.sub_width, self.sub_height = self.sub_menu_bg.get_size()
        self.sub_x = (config.WINDOW_WIDTH - self.sub_width) // 2
        self.sub_y = (config.WINDOW_HEIGHT - self.sub_height) // 2

        buttons = []
        for index, (width, height) in enumerate(self.PRESETS):
            button = Button(
                0,
                self.sub_y + 58 + (index * self.PRESET_SPACING),
                f"{width}x{height}",
                self.PRESET_FONT_SIZE,
                font_color=(163, 88, 48),
                font_path="assets/determination.ttf",
                highlight_color=(92, 45, 28),
            )
            button.rect.size = self.PRESET_BUTTON_SIZE
            button.rect.centerx = self.sub_x + (self.sub_width // 2)
            buttons.append(button)

        super().__init__(state_manager, buttons)
        self.title_font = pygame.font.Font(
            "assets/RamadhanMubarok.otf",
            self.TITLE_FONT_SIZE,
        )

        current_label = self._resolution_text(
            state_manager.get_display_resolution()
        )
        current_button = next(
            button for button in self.buttons
            if button.text == current_label
        )
        self._set_selected_button(current_button)

    @staticmethod
    def _resolution_text(resolution):
        width, height = resolution
        return f"{width}x{height}"

    def update(self):
        # The Settings state underneath this modal already updates the scene.
        pass

    def draw(self, screen):
        overlay = pygame.Surface(config.LOGICAL_SIZE)
        overlay.fill((0, 0, 0))
        overlay.set_alpha(100)
        screen.blit(overlay, (0, 0))
        screen.blit(self.sub_menu_bg, (self.sub_x, self.sub_y))

        heading = self.title_font.render(
            "Select Resolution",
            True,
            (163, 88, 48),
        )
        heading_rect = heading.get_rect(
            center=(
                config.WINDOW_WIDTH // 2,
                self.sub_y + self.TITLE_CENTER_Y_OFFSET,
            )
        )
        screen.blit(heading, heading_rect)

        for button in self.buttons:
            self._draw_preset_button(screen, button)

    def _draw_preset_button(self, screen, button):
        text = button.font.render(button.text, True, button.font_color)
        text_rect = text.get_rect(center=button.rect.center)
        screen.blit(text, text_rect)

    def _activate(self, text):
        super()._activate(text)
        resolutions_by_label = {
            self._resolution_text(resolution): resolution
            for resolution in self.PRESETS
        }
        resolution = resolutions_by_label.get(text)
        if resolution is None:
            return

        self.state_manager.set_display_resolution(resolution)
        self.state_manager.pop_state()

    def _on_escape(self):
        self.state_manager.pop_state()
