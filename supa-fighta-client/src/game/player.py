from loader import AssetLoader
import pygame
import config
from server.ws_client import WSClient
from sound_loader import SoundLoader

ACTIONABLE_STATES = ['dash', 'punch', 'parry', 'parry-hit', 'parried']
NO_SFX_STATES = ['walk', 'idle', 'wait', 'hurt', 'win', 'parry-hit', 'parried']
END_STATES = ['hurt', 'win']
DASH_FACTOR = 2.5

class Player:
    def __init__(self, x, y):
        self.player_assets = AssetLoader()
        self.sound_loader = SoundLoader.get_instance()
        self.last_tap_time = {pygame.K_LEFT: 0, pygame.K_RIGHT: 0}
        self._inputs = []
        self.player_x = x
        self.player_y = y
        self.speed = 2
        self.player_state ='wait'
        self.velocity = 0
        self.hurt_x=None
        self.hurt_done=False
        self.net = WSClient(config.WS_URL)
        self.recovery_until = 0
    def handle_keys(self):
        keys = pygame.key.get_pressed()
        now = pygame.time.get_ticks()

        if now < self.recovery_until:
            return

        self.player_state = 'idle' 
        self.velocity = 0
        
        if keys[pygame.K_SPACE]:
            if self.player_state != 'punch':
                self.player_state = 'punch'
                # TODO: Use Player State to Fetch Assets
                self.player_assets.get_animation('punch').reset()
                self.recovery_until = now + config.RECOVERY_DURATIONS.get('punch', 0)
        if keys[pygame.K_a]:
            if self.player_state != "parry":
                self.player_state = "parry"
                self.player_assets.get_animation('parry').reset()
                self.recovery_until = now + config.RECOVERY_DURATIONS.get('parry', 0)
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

    def update(self, opponent_walking_in: bool, game_over: bool):
        self.player_assets.get_animation(self.player_state).update()
        if self.player_state not in NO_SFX_STATES:
            self.sound_loader.get_sound(self.player_state).play()
        new_x = self.player_x + self.velocity
        
        if not game_over:
            sprite_width = 80
            if new_x < 0:
                new_x = 0
            elif new_x > config.WINDOW_WIDTH - sprite_width*2:
                new_x = config.WINDOW_WIDTH - sprite_width*2
            self.player_x = new_x

        if self.player_state in ACTIONABLE_STATES:
            if self.player_assets.get_animation(self.player_state).is_finished():
                self.player_state = 'idle'
        elif self.player_state in END_STATES:   
            if self.player_state == 'hurt' and self.hurt_x is not None:
                if self.player_x > self.hurt_x - 8:
                    self.player_x -= 2
                else:
                    self.hurt_done=True
            if self.player_assets.get_animation(self.player_state).is_finished():
                pass
        else:
            if not opponent_walking_in and not game_over:
                self.handle_keys()
    
        if self.player_state in ['walk', 'dash']:
            player_state_mod = self.player_state + ('_right' if self.velocity > 0 else '_left')
            self._inputs.append(player_state_mod)

        else:
            self._inputs.append(self.player_state)

    def draw(self, surface):
        self.player_assets.get_animation(self.player_state).draw(surface, (self.player_x, self.player_y))
    
    def waiting_animation(self):
        self.player_assets.get_animation('wait').update()

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
    
    def reset_position(self, x):
        print(f"Resetting player to server position x={x}")
        self.player_x = x
    
    def set_state(self, state: str):
        self.player_state = state

    def set_hurt(self, x_pos: int):
        self.hurt_x = x_pos

    def get_hurt_done(self) -> bool:
        return self.hurt_done
    
    def player_reset(self):
        self.hurt_x = None
        self.hurt_done = False
        self.player_state = 'wait'
        self.player_x = (config.WINDOW_WIDTH // 2) - 120
        self.last_tap_time = {pygame.K_LEFT: 0, pygame.K_RIGHT: 0}
        self._inputs = []
        self.recovery_until = 0
        self.player_assets.get_animation('win').reset()
        self.player_assets.get_animation('hurt').reset()