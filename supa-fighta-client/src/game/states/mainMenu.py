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
            Button(22,config.WINDOW_HEIGHT - 190,"Join Lobby"),
            Button(22,config.WINDOW_HEIGHT - 150,"Settings"),
            Button(25,config.WINDOW_HEIGHT - 110,"Exit")
        ]
        self.background_sprites = SpriteSheet("./supa-fighta-client/assets/background.png").get_sprites(config.WINDOW_WIDTH, config.WINDOW_HEIGHT, 1, 8)
        self.background = Animator(self.background_sprites, 6)
    def enter(self):
        self.running = True
    def exit(self):
        self.running = False
    def update(self):
        self.background.update()
    def draw(self, screen: pygame.Surface):
        self.background.draw(screen)
        for button in self.buttons:
            button.draw(screen)
    def handle_event(self, event):
        for button in self.buttons:
            result = button.handle_event(event)
            if result == "Join Lobby":
                self.state_manager.change_state("lobby")
            elif result == "Settings":
                self.state_manager.change_state("settings")
            elif result == "Exit":
                pygame.event.post(pygame.event.Event(pygame.QUIT))