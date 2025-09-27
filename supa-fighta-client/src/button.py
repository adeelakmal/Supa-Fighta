import pygame

class Button:
    def __init__(self, x, y, text, font_color=(216, 138, 97)):
        self.font = pygame.font.Font("./supa-fighta-client/assets/RamadhanMubarok.otf", 30)
        self.font_color = font_color
        self.rect = pygame.Rect(x, y, 100, 25)
        self.text = text
        self.is_hovered = False
        self.shadow_color = (23, 23, 23)
        self.shadow_offset = 1

    def draw(self, screen):
        # Order of drawing matters, shadow first
        shadow_surface = self.font.render(self.text, True, self.shadow_color)
        screen.blit(shadow_surface, (self.rect.x + self.shadow_offset, self.rect.y + self.shadow_offset))
        
        button_surface = self.font.render(self.text, True, self.font_color)
        screen.blit(button_surface, (self.rect.x, self.rect.y))
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
            self.font_color = (244, 186, 98) if self.is_hovered else (216, 138, 97)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.is_hovered and event.button == 1:
                return self.text
        return None



