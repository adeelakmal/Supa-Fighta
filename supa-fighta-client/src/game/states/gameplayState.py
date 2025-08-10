from game.player import Player
import pygame
import config

class GameplayState:
    def __init__(self, net):
        self.running = True
        self.player = Player(config.WINDOW_WIDTH // 2, config.WINDOW_HEIGHT // 2, net)
        self.background = pygame.image.load("./supa-fighta-client/assets/background.png").convert()

    def enter(self):
        self.running = True
    def exit(self):
        self.running = False
    def update(self):
        self.player.update()
        
    def draw(self, screen: pygame.Surface):
        screen.blit(self.background, (0, 0))
        self.player.draw(screen)
    def handle_event(self,event):
        pass