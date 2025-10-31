import pygame
from animations.sprites import SpriteSheet

class Animator:
    def __init__(self, spritesheet: SpriteSheet, frame_rate, loop=True, flipped=False):
        self.spritesheet = spritesheet
        self.sprites = spritesheet.get_sprites(flipped)
        self.frame_rate = frame_rate
        self.loop = loop
        self.current_frame = 0
        self.last_update = pygame.time.get_ticks()
        self.finished = False

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > 1000 / self.frame_rate:
            self.current_frame += 1
            if self.current_frame >= len(self.sprites):
                if self.loop:
                    self.current_frame = 0
                else:
                    self.current_frame = len(self.sprites) - 1
                    self.finished = True
            self.last_update = now 
    
    def draw(self, surface, position=(0, 0)):
        sprite = self.sprites[self.current_frame]
        sprite.draw(surface, position)

    def is_finished(self):
        return self.finished
    def reset(self):
        self.current_frame = 0
        self.finished = False
        self.last_update = pygame.time.get_ticks()
    def get_current_sprite(self):
        return self.sprites[self.current_frame]
