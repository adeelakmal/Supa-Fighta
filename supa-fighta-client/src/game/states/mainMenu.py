import pygame
import config
from button import Button
from game.states.classes.baseMenu import BaseMenu
from game.states.nameMenu import NameMenuState

class MainMenuState(BaseMenu):
    def __init__(self, state_manager):
        buttons = [
            Button(22, 145, "Join Lobby", 28),
            Button(22, 181, "Player Name", 28),
            Button(22, 217, "Sound On", 28),
            Button(22, 253, "Settings", 28),
            Button(25, 289, "Exit", 28)
        ]
        super().__init__(state_manager, buttons)
        self.title_font = pygame.font.Font("assets/RamadhanMubarok.otf", 44)
        self.heading_font = pygame.font.Font("assets/determination.ttf", 16)
        self.text_font = pygame.font.Font("assets/determination.ttf", 11)
        self.small_font = pygame.font.Font("assets/determination.ttf", 9)

    def draw(self, screen: pygame.Surface):
        self._sync_sound_button()
        super().draw(screen)

        title = self.title_font.render(
            "Supa Fighta",
            True,
            (244, 186, 98)
        )
        screen.blit(title, (20, 38))
        tagline = self.text_font.render(
            "ONE CLEAN HIT WINS",
            True,
            (235, 218, 195)
        )
        screen.blit(tagline, (23, 92))

        self._draw_info_panel(screen)
        self._draw_controls_panel(screen)

        hint = self.text_font.render(
            "UP/DOWN Navigate   ENTER Select   ESC Exit",
            True,
            (225, 214, 199)
        )
        screen.blit(hint, (18, config.WINDOW_HEIGHT - 20))

    def _draw_panel(self, screen, rect):
        panel = pygame.Surface(rect.size, pygame.SRCALPHA)
        panel.fill((25, 18, 15, 155))
        pygame.draw.rect(
            panel,
            (216, 138, 97, 190),
            panel.get_rect(),
            1,
            border_radius=6
        )
        screen.blit(panel, rect)

    def _draw_info_panel(self, screen):
        panel_rect = pygame.Rect(446, 26, 172, 40)
        self._draw_panel(screen, panel_rect)

        player_label = self.text_font.render(
            f"PLAYER   {config.PLAYER_NAME}",
            True,
            (245, 235, 220)
        )
        screen.blit(player_label, (panel_rect.x + 12, panel_rect.y + 12))

    def _draw_controls_panel(self, screen):
        panel_rect = pygame.Rect(390, 102, 228, 166)
        self._draw_panel(screen, panel_rect)

        heading = self.heading_font.render(
            "CONTROLS",
            True,
            (244, 186, 98)
        )
        screen.blit(heading, (panel_rect.x + 12, panel_rect.y + 11))

        controls = (
            ("LEFT / RIGHT", "Move"),
            ("LEFT / RIGHT TWICE", "Dash"),
            ("SPACE", "Punch"),
            ("A", "Parry")
        )
        for index, (key, action) in enumerate(controls):
            y = panel_rect.y + 40 + (index * 28)
            key_rect = pygame.Rect(panel_rect.x + 12, y, 124, 21)
            pygame.draw.rect(
                screen,
                (66, 45, 36),
                key_rect,
                border_radius=4
            )
            pygame.draw.rect(
                screen,
                (216, 138, 97),
                key_rect,
                1,
                border_radius=4
            )
            key_text = self.small_font.render(
                key,
                True,
                (250, 235, 215)
            )
            key_text_rect = key_text.get_rect(center=key_rect.center)
            action_text = self.text_font.render(
                action,
                True,
                (245, 235, 220)
            )
            screen.blit(key_text, key_text_rect)
            screen.blit(
                action_text,
                (panel_rect.x + 148, y + 5)
            )

    def _sync_sound_button(self):
        sound_button = next(
            button
            for button in self.buttons
            if button.text.startswith("Sound ")
        )
        sound_button.set_text(self.sound_loader.get_status_text())

    def _activate(self, text):
        super()._activate(text)
        if text == "Join Lobby":
            self.state_manager.change_state("lobby")
        elif text == "Player Name":
            self.state_manager.push_state(NameMenuState(self.state_manager))
        elif text.startswith("Sound "):
            self.sound_loader.toggle_mute()
            self._sync_sound_button()
        elif text == "Settings":
            self.state_manager.change_state("settings")
        elif text == "Exit":
            pygame.event.post(pygame.event.Event(pygame.QUIT))

    def _on_escape(self):
        pygame.event.post(pygame.event.Event(pygame.QUIT))
