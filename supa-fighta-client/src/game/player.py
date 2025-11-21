from loader import AssetLoader
import pygame
import config
from server.ws_client import WSClient

ACTIONABLE_STATES = ['dash', 'punch', 'parry']
DASH_FACTOR = 2.5

class Player:
    def __init__(self, x, y):
        self.player_assets = AssetLoader()
        self.last_tap_time = {pygame.K_LEFT: 0, pygame.K_RIGHT: 0}
        self._inputs = []
        self.player_x = x
        self.player_y = y
        self.speed = 2
        self.player_state ='idle'
        self.velocity = 0
        self.net = WSClient(config.WS_URL)
    def handle_keys(self):
        keys = pygame.key.get_pressed()
        now = pygame.time.get_ticks()

        self.player_state = 'idle' 
        self.velocity = 0
        
        if keys[pygame.K_SPACE]:
            if self.player_state != 'punch':
                self.player_state = 'punch'
                self.player_assets.get_animation('punch').reset()
        if keys[pygame.K_a]:
            if self.player_state != "parry":
                self.player_state = "parry"
                self.player_assets.get_animation('parry').reset()
        if keys[pygame.K_LEFT]:
            delta_left_tap = now - self.last_tap_time[pygame.K_LEFT]
            if (30 < delta_left_tap < 200) and (self.player_state != 'dash'):
                self.player_state = 'dash'
                self.player_assets.get_animation('dash').reset()
            else:
                self.player_state = 'walk'
            self.velocity = -self.speed * ((DASH_FACTOR-0.5) if self.player_state == 'dash' else 1)
            self.last_tap_time[pygame.K_LEFT] = now
        if keys[pygame.K_RIGHT]:
            delta_right_tap = now - self.last_tap_time[pygame.K_RIGHT]
            if (30 < delta_right_tap < 200) and (self.player_state != 'dash'):
                self.player_state = 'dash'
                self.player_assets.get_animation('dash').reset()
            else:
                self.player_state = 'walk'
            self.velocity = self.speed * (DASH_FACTOR if self.player_state == 'dash' else 1)
            self.last_tap_time[pygame.K_RIGHT] = now
        if self.player_state in ['walk', 'dash']:
            player_state_mod = self.player_state + ('_left' if self.velocity > 0 else '_right')
            self._inputs.append(player_state_mod)

        else:
            self._inputs.append(self.player_state)

    def update(self):
        self.player_assets.get_animation(self.player_state).update()
        new_x = self.player_x + self.velocity
        sprite_width = 80
        if new_x < 0:
            new_x = 0
        elif new_x > config.WINDOW_WIDTH - sprite_width*2:
            new_x = config.WINDOW_WIDTH - sprite_width*2
        self.player_x = new_x

        if self.player_state in ACTIONABLE_STATES:
            if self.player_assets.get_animation(self.player_state).is_finished():
                self.player_state = 'idle'
        else:
            self.handle_keys()

    def draw(self, surface):
        self.player_assets.get_animation(self.player_state).draw(surface, (self.player_x, self.player_y))
    
    def waiting_animation(self):
        self.player_assets.get_animation('idle').update()

    def get_hurtbox(self) -> pygame.Rect:
        asset_hurtbox = self.player_assets.get_hurtbox(self.player_state)
        if not asset_hurtbox:
            return None
        hurtbox = pygame.Rect(
            self.player_x,
            self.player_y,
            asset_hurtbox[0],
            asset_hurtbox[1],
        )
        return hurtbox

    def get_hitbox(self) -> pygame.Rect:
        asset_hitbox = self.player_assets.get_hitbox(self.player_state)
        if not asset_hitbox:
            return None
        hitbox = pygame.Rect(
            self.player_x + asset_hitbox[0],
            self.player_y + asset_hitbox[1],
            asset_hitbox[2],
            asset_hitbox[3],
        )
        return hitbox