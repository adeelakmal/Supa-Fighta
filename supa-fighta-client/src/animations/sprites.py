import pygame
from typing import List
import config
from type.sprite import SpriteProperties


class SpriteSheet:
    def __init__(self, properties: SpriteProperties):
        self.sheet = pygame.image.load(properties.path).convert_alpha()
        self.sprites: List[Sprite] = []
        self.properties = properties
    def get_sprite(self, x, y, width, height):
        sprite = pygame.Surface((width, height), pygame.SRCALPHA)
        sprite.blit(self.sheet, (0,0), (x, y, width, height))
        return sprite
    def get_sprites(self, flipped = False):
        rows = self.properties.rows
        cols = self.properties.cols
        sprite_width = self.properties.width
        sprite_height = self.properties.height
        for row in range(rows):
            for col in range(cols):
                x = col * sprite_width
                y = row * sprite_height
                sprite = Sprite(
                    image = self.get_sprite(x, y, sprite_width, sprite_height),
                )
                self.sprites.append(sprite)
        if flipped:
            self.flip_sprites()
        return self.sprites
    def flip_sprites(self):
        for sprite in self.sprites:
            sprite.flip()
    
class Sprite:
    def __init__(self, image: pygame.Surface):
        self.image = image

    def draw(self, surface: pygame.Surface, position):
        surface.blit(self.image, position)

    def flip(self):
        self.image = pygame.transform.flip(self.image, True, False)
