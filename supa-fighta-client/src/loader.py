import config
from animations.sprites import SpriteSheet
from animations.animation import Animator
from type.sprite import SpriteProperties

class AssetLoader:
    def __init__(self, flipped=False):
        self.sprites = [] 
        self.animations = {}
        for name, properties in config.SPRITES.items():
            properties = SpriteProperties(**properties)
            sprite_sheet = SpriteSheet(properties.path)
            sprite_sheet.get_sprites(properties)
            if flipped:
                sprite_sheet.flip_sprites()
                self.sprites.append(sprite_sheet)
            else:
                self.sprites.append(sprite_sheet)

            self.animations[name] = Animator(sprite_sheet.sprites, frame_rate=properties.frame_rate, loop=properties.loop)

    def get_animation(self, name: str) -> Animator:
        return self.animations.get(name)
    
    def get_hitbox(self, name: str):
        animator = self.get_animation(name)
        if animator and animator.sprites:
            return animator.sprites[animator.current_frame].get_hitbox()
        return None
    
    def get_hurtbox(self, name: str):
        animator = self.get_animation(name)
        if animator and animator.sprites:
            return animator.sprites[animator.current_frame].get_hurtbox()
        return None
