import pygame
import config

class NameMenuState:
    def __init__(self, state_manager):
        self.state_manager = state_manager
        self.player_name_input = config.PLAYER_NAME
        self.sub_menu_bg = pygame.image.load("assets/sub_menu.png").convert_alpha()
        self.textfield = pygame.image.load("assets/textfield.png").convert_alpha()
        self.held_key = None
        self.key_tick = 0
        self.key_delay = 16
        self.backspace_held = False
        self.backspace_tick = 0
        self.backspace_delay = 10
        self.cursor_visible = True
        self.cursor_timer = 0

    def update(self):
        self.cursor_timer += 1
        if self.cursor_timer > 30:
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer = 0
        if self.held_key and not self.backspace_held:
            self.key_tick += 1
            if self.key_tick >= self.key_delay:
                if len(self.player_name_input) < 20:
                    self.player_name_input += self.held_key
                self.key_tick = 0
                self.key_delay = max(3, self.key_delay - 4)
        if self.backspace_held:
            self.backspace_tick += 1
            if self.backspace_tick >= self.backspace_delay:
                if len(self.player_name_input) > 0:
                    self.player_name_input = self.player_name_input[:-1]
                self.backspace_tick = 0
                self.backspace_delay = max(2, self.backspace_delay - 2)

    def draw(self, screen):
        # dark overlay
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
        # heading
        font = pygame.font.Font("assets/RamadhanMubarok.otf", 40)
        heading = font.render("Enter Player Name", True, (163, 88, 48))
        screen.blit(
            heading,
            (sub_x + (sub_width - heading.get_width()) // 2, sub_y + 40)
        )
        # textfield
        input_font = pygame.font.Font("assets/determination.ttf", 16)
        input_w, input_h = self.textfield.get_size()
        input_rect = pygame.Rect(sub_x + 40, sub_y + 90, input_w, input_h)
        screen.blit(self.textfield, input_rect)
        display_text = self.player_name_input
        input_text = input_font.render(display_text, True, (163, 88, 48))
        # clip view only (DO NOT modify actual string)
        while input_text.get_width() > input_rect.width - 20:
            display_text = display_text[1:]
            input_text = input_font.render(display_text, True, (163, 88, 48))
        text_x = input_rect.x + (input_rect.width - input_text.get_width()) // 2
        text_y = input_rect.y + (input_rect.height - input_text.get_height()) // 2
        screen.blit(input_text, (text_x, text_y))
        # cursor
        if self.cursor_visible:
            pygame.draw.rect(
                screen,
                (163, 88, 48),
                (text_x + input_text.get_width() + 1, text_y, 2, input_text.get_height() - 1)
            )

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.state_manager.pop_state()
            elif event.key == pygame.K_RETURN:
                self._save_and_exit()
            elif event.key == pygame.K_BACKSPACE:
                if len(self.player_name_input) > 0:
                    self.player_name_input = self.player_name_input[:-1]
                self.backspace_held = True
                self.backspace_tick = 0
                self.backspace_delay = 10
            else:
                if event.unicode.isprintable():
                    if len(self.player_name_input) < 20:
                        self.player_name_input += event.unicode
                    self.held_key = event.unicode
                    self.key_tick = 0
                    self.key_delay = 16
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_BACKSPACE:
                self.backspace_held = False
                self.backspace_tick = 0
                self.backspace_delay = 10
            if self.held_key and event.unicode == self.held_key:
                self.held_key = None
                self.key_tick = 0
                self.key_delay = 16

    def _save_and_exit(self):
        config.PLAYER_NAME = self.player_name_input
        self.state_manager.pop_state()