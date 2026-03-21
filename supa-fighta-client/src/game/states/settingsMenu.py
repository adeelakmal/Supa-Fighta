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

        # typing behaviour
        self.held_key = None
        self.key_tick = 0
        self.key_delay = 20

        # backspace behaviour
        self.backspace_held = False
        self.backspace_tick = 0
        self.backspace_delay = 12

        # cursor
        self.cursor_visible = True
        self.cursor_timer = 0

    def update(self):
        super().update()

        if not self.sub_menu_active:
            return

        # blinking cursor
        self.cursor_timer += 1
        if self.cursor_timer > 30:
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer = 0

        # held character typing
        if self.held_key and not self.backspace_held:
            self.key_tick += 1

            if self.key_tick >= self.key_delay:
                if len(self.player_name_input) < 20:
                    self.player_name_input += self.held_key

                self.key_tick = 0
                self.key_delay = max(3, self.key_delay - 4)

        # accelerating backspace
        if self.backspace_held:
            self.backspace_tick += 1

            if self.backspace_tick >= self.backspace_delay:
                if len(self.player_name_input) > 0:
                    self.player_name_input = self.player_name_input[:-1]

                self.backspace_tick = 0
                self.backspace_delay = max(2, self.backspace_delay - 2)

    def draw(self, screen: pygame.Surface):

        if self.sub_menu_active:

            super().draw(screen)

            background = screen.copy()
            small = pygame.transform.smoothscale(
                background,
                (config.WINDOW_WIDTH // 4, config.WINDOW_HEIGHT // 4)
            )

            blurred = pygame.transform.smoothscale(
                small,
                (config.WINDOW_WIDTH, config.WINDOW_HEIGHT)
            )

            screen.blit(blurred, (0, 0))

            overlay = pygame.Surface((config.WINDOW_WIDTH, config.WINDOW_HEIGHT))
            overlay.fill((0, 0, 0))
            overlay.set_alpha(100)
            screen.blit(overlay, (0, 0))

            sub_width = int(config.WINDOW_WIDTH * 0.5)
            sub_height = int(config.WINDOW_HEIGHT * 0.5)

            sub_x = (config.WINDOW_WIDTH - sub_width) // 2
            sub_y = (config.WINDOW_HEIGHT - sub_height) // 2

            bg = pygame.transform.smoothscale(self.sub_menu_bg, (sub_width, sub_height))
            screen.blit(bg, (sub_x, sub_y))

            heading_font = pygame.font.Font("assets/RamadhanMubarok.otf", 40)

            heading = heading_font.render(
                "Enter Player Name",
                True,
                (163, 88, 48)
            )

            heading_x = sub_x + (sub_width - heading.get_width()) // 2
            screen.blit(heading, (heading_x, sub_y + 40))

            # textfield
            input_font = pygame.font.Font("assets/determination.ttf", 16)

            input_w, input_h = self.textfield.get_size()

            input_rect = pygame.Rect(
                sub_x + 40,
                sub_y + 90,
                input_w,
                input_h
            )

            screen.blit(self.textfield, input_rect)

            display_text = self.player_name_input

            input_text = input_font.render(display_text, True, (163, 88, 48))

            # clip text if too long
            while input_text.get_width() > input_rect.width - 20:
                display_text = display_text[1:]
                input_text = input_font.render(display_text, True, (163, 88, 48))

            text_x = input_rect.x + (input_rect.width - input_text.get_width()) // 2
            text_y = input_rect.y + (input_rect.height - input_text.get_height()) // 2

            screen.blit(input_text, (text_x, text_y))

            # cursor
            if self.cursor_visible:

                cursor_x = text_x + input_text.get_width() + 1
                cursor_y = text_y

                pygame.draw.rect(
                    screen,
                    (163, 88, 48),
                    (cursor_x, cursor_y, 2, input_text.get_height()-1)
                )

        else:
            super().draw(screen)

    def handle_event(self, event):

        if self.sub_menu_active:

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_ESCAPE:
                    self.sub_menu_active = False

                elif event.key == pygame.K_RETURN:
                    self._save_name()

                elif event.key == pygame.K_BACKSPACE:

                    if len(self.player_name_input) > 0:
                        self.player_name_input = self.player_name_input[:-1]

                    self.backspace_held = True
                    self.backspace_tick = 0
                    self.backspace_delay = 12

                else:

                    if event.unicode.isprintable():

                        if len(self.player_name_input) < 20:
                            self.player_name_input += event.unicode

                        self.held_key = event.unicode
                        self.key_tick = 0
                        self.key_delay = 20

            if event.type == pygame.KEYUP:

                if event.key == pygame.K_BACKSPACE:
                    self.backspace_held = False
                    self.backspace_tick = 0
                    self.backspace_delay = 12

                if self.held_key and event.unicode == self.held_key:
                    self.held_key = None
                    self.key_tick = 0
                    self.key_delay = 20

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
            pass

        elif text == "Back":
            self._go_back()

    def _on_escape(self):
        self._go_back()

    def _go_back(self):
        self.state_manager.go_back()