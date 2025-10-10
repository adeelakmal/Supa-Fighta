import pygame
from animations.sprites import SpriteSheet
from animations.animation import Animator

class AssetLoader:
    def __init__(self, flipped=False):
        # SpriteSheets
        self.idle_sheet = SpriteSheet("./supa-fighta-client/assets/Idel.png")
        self.walk_sheet = SpriteSheet("./supa-fighta-client/assets/Walk.png")
        self.dash_sheet = SpriteSheet("./supa-fighta-client/assets/Dash.png")
        self.punch_sheet = SpriteSheet("./supa-fighta-client/assets/Punch.png")
        self.parry_sheet = SpriteSheet("./supa-fighta-client/assets/Parry.png")

        # Sprites
        self.idle_sprites = self.idle_sheet.get_sprites(120, 120, 1, 5)
        self.walk_sprites = self.walk_sheet.get_sprites(120, 120, 1, 5)
        self.dash_sprites = self.dash_sheet.get_sprites(120, 120, 1, 5)
        self.punch_sprites = self.punch_sheet.get_sprites(120, 120, 1, 9)
        self.parry_sprites = self.parry_sheet.get_sprites(120, 120, 1, 5)

        if flipped:
            self.idle_sprites = self.idle_sheet.flip_sprites()
            self.walk_sprites = self.walk_sheet.flip_sprites()
            self.dash_sprites = self.dash_sheet.flip_sprites()
            self.punch_sprites = self.punch_sheet.flip_sprites()
            self.parry_sprites = self.parry_sheet.flip_sprites()

        # Animators
        self.animations = {
            "idle": Animator(self.idle_sprites, frame_rate=15, loop=True),
            "walk": Animator(self.walk_sprites, frame_rate=15, loop=True),
            "dash": Animator(self.dash_sprites, frame_rate=20, loop=False),
            "punch": Animator(self.punch_sprites, frame_rate=25, loop=False),
            "parry": Animator(self.parry_sprites, frame_rate=15, loop=False),
        }

    def get_animation(self, name: str) -> Animator:
        return self.animations.get(name)

# Usage example (import and instantiate once, then reuse):
# loader = AssetLoader()
# walk_anim = loader.get_animation("walk")