import pygame
from sound_loader import SoundLoader

class Button:
    def __init__(self, x, y, text, font_color=(216, 138, 97)):
        self.font = pygame.font.Font("./supa-fighta-client/assets/RamadhanMubarok.otf", 30)
        self.default_color = font_color
        self.font_color = font_color
        self.rect = pygame.Rect(x, y, 100, 25)
        self.text = text
        self.is_hovered = False
        self.is_selected = False
        self.shadow_color = (23, 23, 23)
        self.shadow_offset = 1
        self.sound_loader = SoundLoader.get_instance()

    def draw(self, screen):
        shadow_surface = self.font.render(self.text, True, self.shadow_color)
        screen.blit(
            shadow_surface,
            (self.rect.x + self.shadow_offset, self.rect.y + self.shadow_offset)
        )
        button_surface = self.font.render(self.text, True, self.font_color)
        screen.blit(button_surface, (self.rect.x, self.rect.y))

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
            if self.is_hovered:
                self.font_color = (244, 186, 98)
            elif not self.is_selected:
                self.font_color = self.default_color
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.is_hovered and event.button == 1:
                return self.text
        return None

    def set_selected(self, selected: bool):
        self.is_selected = selected
        self.font_color = (244, 186, 98) if selected else self.default_color
