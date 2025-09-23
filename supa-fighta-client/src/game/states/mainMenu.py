import pygame
import config
from src.game.stateManager import GameState

class MainMenuState:
    def __init__(self, state_manager: GameState):
        self.state_manager = state_manager
        self.title_font = pygame.font.Font(None,74)
        self.button_font = pygame.font.Font(None, 36)
        self.buttons = {
            "start_game":pygame.Rect((config.WINDOW_WIDTH/2)-100,100,200,50),
            "settings":pygame.Rect((config.WINDOW_WIDTH/2)-100,160,200,50),
            "exit":pygame.Rect((config.WINDOW_WIDTH/2)-100,220,200,50)
        }
    def enter(self):
        self.running = True
    def exit(self):
        self.running = False
    def update(self):
        pass
    def draw(self, screen: pygame.Surface):
        screen.fill((255, 255, 255))
        title_surface = self.title_font.render("Supa Fighta", True, (0, 0, 0))
        rect = title_surface.get_rect(center=(config.WINDOW_WIDTH //2 , 50)) # Center the title
        screen.blit(title_surface, rect)
        for button, rect in self.buttons.items():
            pygame.draw.rect(screen, (0, 0, 255), rect)
            button_surface = self.button_font.render(button.replace("_", " ").title(), True, (255, 255, 255))
            screen.blit(button_surface, (rect.x + 10, rect.y + 10))
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                mouse_pos = event.pos
                for button, rect in self.buttons.items():
                    if rect.collidepoint(mouse_pos):
                        if button == "start_game":
                            self.state_manager.change_state("gameplay")
                        elif button == "settings":
                            self.state_manager.change_state("settings")
                        elif button == "exit":
                            pygame.quit()
                            exit()

