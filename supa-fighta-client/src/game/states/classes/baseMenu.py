import pygame
import config
from sound_loader import SoundLoader

class BaseMenu:
    def __init__(self, state_manager, buttons):
        self.state_manager = state_manager
        self.buttons = buttons
        self.selected_button = self.buttons[0] if self.buttons else None
        self.using_mouse = False
        self.sound_loader = SoundLoader.get_instance()
        # delegate visual/audio selection behavior to Button
        if self.selected_button:
            self.selected_button.set_selected(True)

    def enter(self):
        if not pygame.mixer.music.get_busy():
            pygame.mixer.music.load(config.MUSIC["menu"])
            pygame.mixer.music.play(-1, 0, 0)

    def exit(self):
        self._set_selected_button(self.buttons[0])

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
                self._activate(self.selected_button.text)
            elif event.key == pygame.K_ESCAPE:
                self._on_escape()

        # Handle mouse events for buttons
        for i, button in enumerate(self.buttons):
            result = button.handle_event(event)
            if event.type == pygame.MOUSEMOTION and button.is_hovered:
                if self.selected_button != button:
                    self.using_mouse = True
                    self._set_selected_button(button)
            if result:
                self._activate(result)

    def _set_selected_button(self, button):
        if button == self.selected_button:
            return
        self.selected_button.set_selected(False)
        self.selected_button = button
        self.selected_button.set_selected(True)

    def _move_selection(self, direction):
        current_index = self.buttons.index(self.selected_button)
        new_index = (current_index + direction) % len(self.buttons)
        self._set_selected_button(self.buttons[new_index])

    def _activate(self, text):
        """
        Delegate activation feedback to the Button instance. Find the
        button matching the provided text and call its activate() so the
        Button class controls the sound/visuals.
        """
        try:
            matching = next((b for b in self.buttons if b.text == text), None)
            if matching:
                matching.activate()
            elif self.selected_button:
                # fallback to currently selected button
                self.selected_button.activate()
        except Exception:
            pass

    def _on_escape(self):
        pass
