import pygame
from typing import List
import config
from type.sprite import SpriteProperties


class SpriteSheet:
    def __init__(self, filename):
        self.sheet = pygame.image.load(filename).convert_alpha()
        self.sprites: List[Sprite] = []
    def get_sprite(self, x, y, width, height):
        sprite = pygame.Surface((width, height), pygame.SRCALPHA)
        sprite.blit(self.sheet, (0,0), (x, y, width, height))
        return sprite
    def get_sprites(self, sprite_properties: SpriteProperties):
        rows = sprite_properties.rows
        cols = sprite_properties.cols
        sprite_width = sprite_properties.width
        sprite_height = sprite_properties.height
        for row in range(rows):
            for col in range(cols):
                x = col * sprite_width
                y = row * sprite_height
                sprite = Sprite(
                    image = self.get_sprite(x, y, sprite_width, sprite_height),
                    hitbox = sprite_properties.hitbox,
                    hurtbox = sprite_properties.hurtbox,
                )
                self.sprites.append(sprite)
        return self.sprites
    def flip_sprites(self):
        return [sprite.flip() for sprite in self.sprites]
    
class Sprite:
    def __init__(self, image: pygame.Surface, hitbox: pygame.Rect, hurtbox):
        self.image = image
        if hitbox:
            self.hitbox = pygame.Rect(hitbox[0], hitbox[1], hitbox[2], hitbox[3])
            self.current_hitbox =  pygame.Rect(hitbox[0], hitbox[1], hitbox[2], hitbox[3])
        else:
            self.hitbox = None
            self.current_hitbox = None

        if hurtbox:
            self.hurtbox=pygame.Rect(0, 0, hurtbox[0], hurtbox[1])
        else:
            self.hurtbox = None

    def draw_debug(self, surface: pygame.Surface, position):
        # Draw hurtbox in green with alpha
        if self.hurtbox:
            pygame.draw.rect(surface, (0, 255, 0), 
                        pygame.Rect(position[0], 
                                  position[1],
                                  self.hurtbox.width, 
                                  self.hurtbox.height), 1)

        # Draw hitbox in red with alpha
        if self.hitbox:
            pygame.draw.rect(surface, (255, 0, 0), 
                        pygame.Rect(self.current_hitbox.x, 
                                    self.current_hitbox.y,
                                    self.current_hitbox.width, 
                                    self.current_hitbox.height), 1)

    def draw(self, surface: pygame.Surface, position):
        if self.hurtbox:
            self.hurtbox.x = position[0]
            self.hurtbox.y = position[1]
        if self.hitbox:
            self.current_hitbox.x = position[0] + self.hitbox.x
            self.current_hitbox.y = position[1] + self.hitbox.y
        surface.blit(self.image, position)
        if config.DEBUG:
            self.draw_debug(surface, position)

    def flip(self):
        self.image = pygame.transform.flip(self.image, True, False)
    
    def get_hurtbox(self):
        return self.hurtbox
    
    def get_hitbox(self):
        return self.current_hitbox