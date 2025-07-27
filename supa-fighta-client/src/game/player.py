from animations.sprites import SpriteSheet
from animations.animation import Animator
import pygame
import config

ACTIONABLE_STATES = ['dash', 'punch']
DASH_FACTOR = 2.5

class Player:
    def __init__(self, x, y, net):
        self.player_sprites = {
            "idel": SpriteSheet("./supa-fighta-client/assets/Idel.png").get_sprites(120, 120, 1, 5),
            "walk": SpriteSheet("./supa-fighta-client/assets/Walk.png").get_sprites(120, 120, 1, 5),
            "dash": SpriteSheet("./supa-fighta-client/assets/Dash.png").get_sprites(120, 120, 1, 5),
            "punch": SpriteSheet("./supa-fighta-client/assets/Punch.png").get_sprites(120, 120, 1, 9),
        }
        self.player_animations = {
            "idel": Animator(self.player_sprites["idel"], frame_rate=15, loop=True),
            "walk": Animator(self.player_sprites["walk"], frame_rate=15, loop=True),
            "dash": Animator(self.player_sprites["dash"], frame_rate=20, loop=False),
            "punch": Animator(self.player_sprites["punch"], frame_rate=25, loop=False),
        }
        self.last_tap_time = {pygame.K_LEFT: 0, pygame.K_RIGHT: 0}
        self.player_x = x
        self.player_y = y
        self.speed = 2
        self.player_state ='idel'
        self.velocity = 0
        self.net = net
    def handle_keys(self):
        keys = pygame.key.get_pressed()
        now = pygame.time.get_ticks()

        moved = False
        self.player_state = 'idel' 
        self.velocity = 0
        
        if keys[pygame.K_SPACE]:
            if self.player_state != 'punch':
                self.player_state = 'punch'
                self.player_animations['punch'].reset()
  

        if keys[pygame.K_LEFT]:
            delta_left_tap = now - self.last_tap_time[pygame.K_LEFT]
            if (30 < delta_left_tap < 200) and (self.player_state != 'dash'):
                self.player_state = 'dash'
                self.player_animations['dash'].reset()
            else:
                self.player_state = 'walk'
            self.velocity = -self.speed * ((DASH_FACTOR-0.5) if self.player_state == 'dash' else 1)
            moved = True
            self.last_tap_time[pygame.K_LEFT] = now
        if keys[pygame.K_RIGHT]:
            delta_right_tap = now - self.last_tap_time[pygame.K_RIGHT]
            if (30 < delta_right_tap < 200) and (self.player_state != 'dash'):
                self.player_state = 'dash'
                self.player_animations['dash'].reset()
            else:
                self.player_state = 'walk'
            self.velocity = self.speed * (DASH_FACTOR if self.player_state == 'dash' else 1)
            moved = True
            self.last_tap_time[pygame.K_RIGHT] = now

        # if moved:
        #     self.rect.move_ip(dx, dy)    # local prediction
        #     # tell the server; keep the payload tiny
        #     self.net.send("move", {"dx": dx, "dy": dy})
    def update(self):
        self.player_animations[self.player_state].update()
        self.player_x += self.velocity
        if self.player_state in ACTIONABLE_STATES:
            if self.player_animations[self.player_state].is_finished():
                self.player_state = 'idel'
        else:
            self.handle_keys()

    def draw(self, surface):
        self.player_animations[self.player_state].draw(surface, (self.player_x, self.player_y))
