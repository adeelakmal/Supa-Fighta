import pygame

class Animator:
    def __init__(self, sprites, frame_rate, loop=True):
        self.sprites = sprites
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
        surface.blit(sprite, position)

    def is_finished(self):
        return self.finished
    def reset(self):
        self.current_frame = 0
        self.finished = False
        self.last_update = pygame.time.get_ticks()
