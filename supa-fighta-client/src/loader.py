import pygame
import config
from animations.sprites import SpriteSheet
from animations.animation import Animator

class AssetLoader:
    def __init__(self, flipped=False):
        self.sprites = [] 
        self.animations = {}
        for name, properties in config.SPRITES.items():
            sprite_sheet = SpriteSheet(properties["path"])
            sprite_sheet.get_sprites(properties)
            if flipped:
                sprite_sheet.flip_sprites()
                self.sprites.append(sprite_sheet)
            else:
                self.sprites.append(sprite_sheet)

            self.animations[name] = Animator(sprite_sheet.sprites, frame_rate=properties["frame_rate"], loop=properties["loop"])

    def get_animation(self, name: str) -> Animator:
        return self.animations.get(name)
