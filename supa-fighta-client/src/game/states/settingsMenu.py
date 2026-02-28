import pygame
import config
from button import Button
from sound_loader import SoundLoader

class SettingsState:
    def __init__(self, state_manager):
        self.state_manager = state_manager
        self.buttons = [
            Button(15, config.WINDOW_HEIGHT - 190, "Player Name", 30),
            Button(15, config.WINDOW_HEIGHT - 150, "Sound", 30),
            Button(15, config.WINDOW_HEIGHT - 110, "Back", 30)
        ]
        self.selected_index = 0
        self.using_mouse = False
        self.buttons[self.selected_index].set_selected(True)
        self.sound_loader = SoundLoader.get_instance()

    def enter(self):
        if not pygame.mixer.music.get_busy():
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
                self._go_back()

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
        if text == "Username Settings":
            # TODO: Implement username settings
            pass
        elif text == "Sound Settings":
            # TODO: Implement sound settings
            pass
        elif text == "Back":
            self._go_back()

    def _go_back(self):
        self.state_manager.go_back()
