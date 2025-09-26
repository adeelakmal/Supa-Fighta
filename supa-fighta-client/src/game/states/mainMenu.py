import pygame
import config
from animations.sprites import SpriteSheet
from animations.animation import Animator
from button import Button

class MainMenuState:
    def __init__(self, state_manager):
        self.state_manager = state_manager
        self.title_font = pygame.font.Font(None,74)        
        self.buttons = [
            Button(config.WINDOW_WIDTH//2 - 75,config.WINDOW_HEIGHT//2 - 50,"Start Game"),
            Button(config.WINDOW_WIDTH//2 - 75,config.WINDOW_HEIGHT//2,"Settings"),
            Button(config.WINDOW_WIDTH//2 - 75,config.WINDOW_HEIGHT//2 + 50,"Exit")
        ]
        self.background_sprites = SpriteSheet("./supa-fighta-client/assets/background.png").get_sprites(config.WINDOW_WIDTH, config.WINDOW_HEIGHT, 1, 8)
        self.background = Animator(self.background_sprites, 10)
    def enter(self):
        self.running = True
    def exit(self):
        self.running = False
    def update(self):
        self.background.update()
    def draw(self, screen: pygame.Surface):
        self.background.draw(screen)
        title_surface = self.title_font.render("Supa Fighta", True, (0, 0, 0))
        rect = title_surface.get_rect(center=(config.WINDOW_WIDTH //2 , 50)) # Center the title
        screen.blit(title_surface, rect)
        for button in self.buttons:
            button.draw(screen)
    def handle_event(self, event):
        for button in self.buttons:
            result = button.handle_event(event)
            if result == "Start Game":
                self.state_manager.change_state("lobby")
            elif result == "Settings":
                self.state_manager.change_state("settings")
            elif result == "Exit":
                pygame.event.post(pygame.event.Event(pygame.QUIT))