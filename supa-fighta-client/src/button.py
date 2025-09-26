import pygame

class Button:
    def __init__(self, x, y, text, font_color = (255, 255, 255)):
        self.font = pygame.font.Font(None, 36)
        self.font_color = font_color
        self.rect = pygame.Rect(x, y, 150, 40)
        self.text = text
        self.is_hovered = False

    def draw(self, screen):
        pygame.draw.rect(screen, (0, 0, 255), self.rect)
        button_surface = self.font.render(self.text, True, self.font_color)
        screen.blit(button_surface, (self.rect.x + 10, self.rect.y + 10))
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
            self.font_color = (255, 0, 0) if self.is_hovered else (255, 255, 255)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.is_hovered and event.button == 1:
                return self.text
        return None



