import pygame
import config
from sound_loader import SoundLoader

class MenuState:
    def __init__(self, state_manager, buttons):
        self.state_manager = state_manager
        self.buttons = buttons
        self.selected_index = 0
        self.using_mouse = False
        self.sound_loader = SoundLoader.get_instance()
        # Set first button as selected
        if self.buttons:
            self.buttons[self.selected_index].set_selected(True)

    def enter(self):
        pygame.mixer.music.load(config.MUSIC["menu"])
        pygame.mixer.music.play(-1, 0, 0)

    def exit(self):
        pass

    def update(self):
        self.state_manager.update_background()

    def draw(self, screen: pygame.Surface):
        self.state_manager.draw_background(screen)
        for button in self.buttons:
            button.draw(screen)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            self.using_mouse = False
            if event.key == pygame.K_DOWN:
                self._move_selection(1)
            elif event.key == pygame.K_UP:
                self._move_selection(-1)
            elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                self._activate(self.buttons[self.selected_index].text)
            elif event.key == pygame.K_ESCAPE:
                self._on_escape()

        # Handle mouse events for buttons
        for i, button in enumerate(self.buttons):
            result = button.handle_event(event)
            if event.type == pygame.MOUSEMOTION and button.is_hovered:
                if not self.using_mouse or self.selected_index != i:
                    self.using_mouse = True
                    self._set_selected_index(i)
            if result:
                self._activate(result)

    def _set_selected_index(self, index):
        if index == self.selected_index:
            return
        self.buttons[self.selected_index].set_selected(False)
        self.selected_index = index
        self.buttons[self.selected_index].set_selected(True)

    def _move_selection(self, direction):
        new_index = (self.selected_index + direction) % len(self.buttons)
        self._set_selected_index(new_index)
        self.sound_loader.get_sound("button_hover").play()

    def _activate(self, text):
        self.sound_loader.get_sound("button_select").play()

    def _on_escape(self):
        pass
