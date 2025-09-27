import pygame

class SpriteSheet:
    def __init__(self, filename):
        self.sheet = pygame.image.load(filename).convert_alpha()
        self.sprites = []
    def get_sprite(self, x, y, width, height):
        sprite = pygame.Surface((width, height), pygame.SRCALPHA)
        sprite.blit(self.sheet, (0,0), (x, y, width, height))
        return sprite
    def get_sprites(self, sprite_width, sprite_height, rows, cols):
        for row in range(rows):
            for col in range(cols):
                x = col * sprite_width
                y = row * sprite_height
                self.sprites.append(self.get_sprite(x, y, sprite_width, sprite_height))
        return self.sprites
    def flip_sprites(self):
        return [pygame.transform.flip(sprite, True, False) for sprite in self.sprites]