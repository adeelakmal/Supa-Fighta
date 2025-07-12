from game.player import Player
import pygame
import config

class GameplayState:
    def __init__(self, net):
        self.running = True
        self.player = Player(config.WINDOW_WIDTH // 2, config.WINDOW_HEIGHT // 2, net)

    def enter(self):
        self.running = True
    def exit(self):
        self.running = False
    def update(self):
        self.player.update()
        self.player.handle_keys()
        
    def draw(self, screen: pygame.Surface):
        screen.fill(config.BACKGROUND_COLOR)
        self.player.draw(screen)
    def handle_event(self,event):
        pass