import config
from animations.sprites import SpriteSheet
from animations.animation import Animator
from type.sprite import SpriteProperties

class AssetLoader:
    def __init__(self, flipped=False):
        self.animations = {}
        for name, properties in config.SPRITES.items():
            properties = SpriteProperties(**properties)
            self.spritesheet = SpriteSheet(properties)
            self.animations[name] = Animator(self.spritesheet, frame_rate=properties.frame_rate, loop=properties.loop, flipped=flipped)

    def get_animation(self, name: str) -> Animator:
        return self.animations.get(name)
    
    def get_hitbox(self, name: str):
        animator = self.get_animation(name)
        if animator and animator.spritesheet:
            return animator.spritesheet.properties.hitbox
        return None
    
    def get_hurtbox(self, name: str):
        animator = self.get_animation(name)
        if animator and animator.spritesheet:
            return animator.spritesheet.properties.hurtbox
        return None
