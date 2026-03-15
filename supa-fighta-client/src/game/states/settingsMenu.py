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
        self.sub_menu_active = False
        self.player_name_input = config.PLAYER_NAME
        self.save_button = Button(0, 0, "Save", 30)
        self.sub_menu_bg = pygame.image.load("assets/sub_menu.png").convert_alpha()
        self.textfield = pygame.image.load("assets/textfield.png").convert_alpha()

    def draw(self, screen: pygame.Surface):
        if self.sub_menu_active:
            # Draw the main menu first
            super().draw(screen)
            # Create blurred background
            background = screen.copy()
            # Scale down to 1/4
            small = pygame.transform.smoothscale(background, (config.WINDOW_WIDTH // 4, config.WINDOW_HEIGHT // 4))
            # Scale back up to create blur effect
            blurred = pygame.transform.smoothscale(small, (config.WINDOW_WIDTH, config.WINDOW_HEIGHT))
            screen.blit(blurred, (0, 0))
            # Add semi-transparent overlay
            overlay = pygame.Surface((config.WINDOW_WIDTH, config.WINDOW_HEIGHT))
            overlay.fill((0, 0, 0))
            overlay.set_alpha(100)
            screen.blit(overlay, (0, 0))
            # Sub-menu dimensions: smaller, about 40% of screen
            sub_width = int(config.WINDOW_WIDTH * 0.5)
            sub_height = int(config.WINDOW_HEIGHT * 0.5)
            sub_x = (config.WINDOW_WIDTH - sub_width) // 2
            sub_y = (config.WINDOW_HEIGHT - sub_height) // 2
            # Draw sub-menu background from asset
            bg = pygame.transform.smoothscale(self.sub_menu_bg, (sub_width, sub_height))
            screen.blit(bg, (sub_x, sub_y))
            # Heading
            heading_font = pygame.font.Font("assets/RamadhanMubarok.otf", 40)
            heading = heading_font.render("Enter Player Name", True,(163, 88, 48))
            heading2 = heading_font.render("Enter Player Name", True,(0, 0, 0))
            heading_x = sub_x + (sub_width - heading.get_width()) // 2
            # screen.blit(heading2, (heading_x-1, sub_y + 40))
            screen.blit(heading, (heading_x, sub_y + 40))
            # Text field
            input_font = pygame.font.Font("assets/ARIALNB.ttf", 16)
            input_w, input_h = self.textfield.get_size()
            input_rect = pygame.Rect(sub_x + 40, sub_y + 90, input_w, input_h)

            screen.blit(self.textfield, input_rect)

            # Render text
            input_text = input_font.render(self.player_name_input, True, (163, 88, 48))

            # Prevent text overflow (clip from the left if too long)
            while input_text.get_width() > input_rect.width - 10:
                self.player_name_input = self.player_name_input[1:]
                input_text = input_font.render(self.player_name_input, True, (163, 88, 48))

            # Center text vertically
            text_y = input_rect.y + (input_rect.height - input_text.get_height()) // 2

            text_x = input_rect.x + (input_rect.width - input_text.get_width()) // 2
            text_y = input_rect.y + (input_rect.height - input_text.get_height()) // 2

            screen.blit(input_text, (text_x, text_y))
            # Save button, centered
            button_width = 60  # approximate
            # self.save_button.rect.x = sub_x + (sub_width - button_width) // 2
            # self.save_button.rect.y = sub_y + 120
            # self.save_button.draw(screen)
        else:
            super().draw(screen)

    def handle_event(self, event):
        if self.sub_menu_active:
            result = self.save_button.handle_event(event)
            if result == "Save":
                self._save_name()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.sub_menu_active = False
                elif event.key == pygame.K_BACKSPACE:
                    self.player_name_input = self.player_name_input[:-1]
                elif event.key == pygame.K_RETURN:
                    self._save_name()
                else:
                    # Limit characters
                    if len(self.player_name_input) < 20 and event.unicode.isprintable():
                        self.player_name_input += event.unicode
        else:
            super().handle_event(event)

    def _save_name(self):
        config.PLAYER_NAME = self.player_name_input
        self.sub_menu_active = False

    def _activate(self, text):
        super()._activate(text)
        if text == "Player Name":
            self.sub_menu_active = True
            self.player_name_input = config.PLAYER_NAME
        elif text == "Sound":
            # TODO: Implement sound settings
            pass
        elif text == "Back":
            self._go_back()

    def _on_escape(self):
        self._go_back()

    def _go_back(self):
        self.state_manager.go_back()
