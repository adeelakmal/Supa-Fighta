import pygame
import config
from loader import AssetLoader

ACTIONABLE_STATES = ['dash', 'punch', 'parry']
DASH_FACTOR = 2.5

class Opponent:
    def __init__(self, x, y, net):
        self.opponent_x = x
        self.opponent_y = y
        self.opponent_state = 'idle'
        self.opponent_assets = AssetLoader(flipped=True)
        self.speed = 2
        self.velocity = 0        
        # self.net = net
        self.walking_in = True

    def handle_event(self, event):
        self.opponent_state = 'idle'
        self.velocity = 0

        match event:
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
            self.opponent_x += self.velocity
            if self.opponent_state in ACTIONABLE_STATES:
                if self.opponent_assets.get_animation(self.opponent_state).is_finished():
                    self.opponent_state = 'idle'
            else:
                self.handle_event(event="parry") #  for testing purposes only

    def draw(self, surface):
        self.opponent_assets.get_animation(self.opponent_state).draw(surface, (self.opponent_x, self.opponent_y))
    
    def walk_into_frame(self):
        self.walking_in = True

    def get_hurtbox(self):
        return self.opponent_assets.get_animation(self.opponent_state).sprites[self.opponent_assets.get_animation(self.opponent_state).current_frame].get_hurtbox()   

    def get_hitbox(self):
        return self.opponent_assets.get_animation(self.opponent_state).sprites[self.opponent_assets.get_animation(self.opponent_state).current_frame].get_hitbox()