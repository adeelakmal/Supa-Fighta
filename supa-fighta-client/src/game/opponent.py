import pygame
import config
from loader import AssetLoader

ACTIONABLE_STATES = ['dash', 'punch', 'parry']
DASH_FACTOR = 2.5

class Opponent:
    def __init__(self, x, y):
        self.opponent_x = x
        self.opponent_y = y
        self.opponent_state = 'idle'
        self.opponent_assets = AssetLoader(flipped=True)
        self.speed = 2
        self.velocity = 0        
        # self.net = net
        self.walking_in = True

    def handle_event(self, event):

        match event:
            case "idle":
                if self.opponent_state not in ACTIONABLE_STATES:
                    self.opponent_state = 'idle'
                    self.velocity = 0

            case "punch":
                if self.opponent_state != 'punch':
                    self.opponent_state = "punch"
                    self.opponent_assets.get_animation('punch').reset()
            
            case "parry":
                if self.opponent_state != "parry":
                    self.opponent_state = "parry"
                    self.opponent_assets.get_animation('parry').reset()
            
            case "walk_left":
                self.opponent_state = 'walk'
                self.velocity = -self.speed
            
            case "walk_right":
                self.opponent_state = 'walk'
                self.velocity = self.speed
            
            case "dash_left":
                self.opponent_state = 'dash'
                self.opponent_assets.get_animation('dash').reset()
                self.velocity = -self.speed * DASH_FACTOR
            
            case "dash_right":
                self.opponent_state = 'dash'
                self.opponent_assets.get_animation('dash').reset()
                self.velocity = self.speed * DASH_FACTOR
            
            case _:
                pass
    
    def intro_walk(self):        
        if self.opponent_x > config.WINDOW_WIDTH // 2:
            self.opponent_x -= 2  
            self.opponent_state = 'walk'
        else:
            self.opponent_x = config.WINDOW_WIDTH // 2
            self.opponent_state = 'idle'
            self.opponent_assets.get_animation('walk').reset()
            self.walking_in = False

    def update(self):
        self.opponent_assets.get_animation(self.opponent_state).update()
        if self.walking_in:
            self.intro_walk()
        else:
            new_x = self.opponent_x + self.velocity
            sprite_width = 80
            if new_x < sprite_width:
                new_x = sprite_width
            elif new_x > config.WINDOW_WIDTH - sprite_width:
                new_x = config.WINDOW_WIDTH - sprite_width
            self.opponent_x = new_x

            if self.opponent_state in ACTIONABLE_STATES:
                if self.opponent_assets.get_animation(self.opponent_state).is_finished():
                    self.opponent_state = 'idle'

    def draw(self, surface):
        self.opponent_assets.get_animation(self.opponent_state).draw(surface, (self.opponent_x - 40, self.opponent_y)) # Pygames flip is weird can not set anchor point for flipping so i have to subtract half width of sprite from x position to render it in te correct position
    
    def walk_into_frame(self):
        self.walking_in = True

    def get_hurtbox(self) -> pygame.Rect:
        asset_hurtbox = self.opponent_assets.get_hurtbox(self.opponent_state)
        if not asset_hurtbox:
            return None
        hurtbox = pygame.Rect(
            self.opponent_x,
            self.opponent_y,
            asset_hurtbox[0],
            asset_hurtbox[1],
        )
        return hurtbox

    def get_hitbox(self) -> pygame.Rect:
        asset_hitbox = self.opponent_assets.get_hitbox(self.opponent_state)
        if not asset_hitbox:
            return None
        hitbox = pygame.Rect(
            self.opponent_x - asset_hitbox[0]+50,
            self.opponent_y + asset_hitbox[1],
            asset_hitbox[2],
            asset_hitbox[3],
        )
        return hitbox