import pygame
import config
from loader import AssetLoader

class Opponent:
    def __init__(self, x, y, net):
        self.opponent_x = x
        self.opponent_y = y
        self.opponent_state = 'idle'
        self.opponent_assets = AssetLoader(flipped=True)
        # self.net = net
        self.walking_in = False

    def update(self):
        if self.walking_in:
            if self.opponent_x > config.WINDOW_WIDTH // 2:
                self.opponent_x -= 2  
                self.opponent_state = 'walk'
            else:
                self.opponent_x = config.WINDOW_WIDTH // 2
                self.opponent_state = 'idle'
                self.opponent_assets.get_animation('walk').reset()
                self.walking_in = False
        self.opponent_assets.get_animation(self.opponent_state).update()

    def draw(self, surface):
        self.opponent_assets.get_animation(self.opponent_state).draw(surface, (self.opponent_x, self.opponent_y))
    
    def walk_into_frame(self):
        self.walking_in = True  

    def get_hurtbox(self):
        return self.opponent_assets.get_animation(self.opponent_state).sprites[self.opponent_assets.get_animation(self.opponent_state).current_frame].get_hurtbox()   

    def get_hitbox(self):
        return self.opponent_assets.get_animation(self.opponent_state).sprites[self.opponent_assets.get_animation(self.opponent_state).current_frame].get_hitbox()   