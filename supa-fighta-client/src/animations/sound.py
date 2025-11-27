import pygame

class Sound:
    def __init__(self, name, path):
        self.name=name
        self.path=path
        self.audio=pygame.mixer.Sound(path)
    
    def play(self):
        self.audio.play()