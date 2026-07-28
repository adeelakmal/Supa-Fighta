from loader import AssetLoader
import pygame
import config
from server.ws_client import WSClient
from sound_loader import SoundLoader

ACTIONABLE_STATES = ['dash', 'punch', 'parry', 'parry-hit', 'parried']
NO_SFX_STATES = ['walk', 'idle', 'wait', 'hurt', 'win', 'parry-hit', 'parried']
END_STATES = ['hurt', 'win']
DASH_FACTOR = 2.1

class Player:
    def __init__(self, x, y):
        self.player_assets = AssetLoader()
        self.sound_loader = SoundLoader.get_instance()
        self.last_tap_time = {pygame.K_LEFT: 0, pygame.K_RIGHT: 0}
        self._inputs = []
        self.player_x = x
        self.player_y = y
        self.speed = config.PLAYER_MOVE_SPEED
        self.player_state ='wait'
        self.parry_hit_registered = False
        self.attack_resolved = False
        self.queued_state = None
        self.velocity = 0
        self.hurt_x=None
        self.hurt_done=False
        self.net = WSClient(config.WS_URL)
        self.recovery_until = 0
        self.buffered_action = None

    @staticmethod
    def _approach(current, target, amount):
        if current < target:
            return min(current + amount, target)
        if current > target:
            return max(current - amount, target)
        return target

    def _start_action(self, state, now):
        self.enter_state(state)
        self.velocity = 0
        self.recovery_until = (
            now + config.RECOVERY_DURATIONS.get(state, 0)
        )
        self.buffered_action = None

    def _request_action(self, state, now):
        if self.player_state in END_STATES:
            return

        if (
            self.player_state in ACTIONABLE_STATES
            or now < self.recovery_until
        ):
            self.buffered_action = (
                state,
                now + config.INPUT_BUFFER_MS
            )
            return

        self._start_action(state, now)

    def _consume_buffered_action(self, now):
        if self.buffered_action is None:
            return False

        state, expires_at = self.buffered_action
        if now > expires_at:
            self.buffered_action = None
            return False

        if (
            self.player_state in ACTIONABLE_STATES
            or now < self.recovery_until
        ):
            return False

        self._start_action(state, now)
        return True

    def handle_event(self, event):
        if event.type != pygame.KEYDOWN or getattr(event, "repeat", False):
            return

        now = pygame.time.get_ticks()
        if event.key == pygame.K_SPACE:
            self._request_action('punch', now)
            return
        if event.key == pygame.K_a:
            self._request_action('parry', now)
            return
        if event.key not in (pygame.K_LEFT, pygame.K_RIGHT):
            return
        if (
            self.player_state in ACTIONABLE_STATES
            or self.player_state in END_STATES
            or now < self.recovery_until
        ):
            return

        previous_tap = self.last_tap_time[event.key]
        self.last_tap_time[event.key] = now
        if (
            previous_tap > 0
            and now - previous_tap <= config.DOUBLE_TAP_WINDOW_MS
        ):
            direction = -1 if event.key == pygame.K_LEFT else 1
            dash_factor = (
                DASH_FACTOR - 0.5
                if direction < 0
                else DASH_FACTOR
            )
            self.enter_state('dash')
            self.velocity = direction * self.speed * dash_factor
            # A new dash requires two new presses.
            self.last_tap_time[event.key] = 0

    def handle_movement(self):
        keys = pygame.key.get_pressed()
        now = pygame.time.get_ticks()

        if now < self.recovery_until:
            self.velocity = self._approach(
                self.velocity, 0, config.PLAYER_DECELERATION
            )
            return

        direction = int(keys[pygame.K_RIGHT]) - int(keys[pygame.K_LEFT])
        target_velocity = direction * self.speed
        self.player_state = 'walk' if direction else 'idle'

        # Ramp toward the requested speed and ease to a stop when released.
        # Reversing gets extra acceleration so the controls remain responsive.
        if direction == 0:
            self.velocity = self._approach(
                self.velocity, 0, config.PLAYER_DECELERATION
            )
        else:
            acceleration = config.PLAYER_ACCELERATION
            if self.velocity and (self.velocity > 0) != (target_velocity > 0):
                acceleration += config.PLAYER_DECELERATION
            self.velocity = self._approach(
                self.velocity, target_velocity, acceleration
            )

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
                    if self.queued_state:
                        next_state = self.queued_state
                        self.queued_state = None
                        self.enter_state(next_state)
                    else:
                        self.player_state = 'idle'
                    self.parry_hit_registered = False
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
                now = pygame.time.get_ticks()
                if not self._consume_buffered_action(now):
                    self.handle_movement()
    
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
        if self.player_state != 'punch' or self.attack_resolved:
            return None
        animation = self.player_assets.get_animation('punch')
        active_start, active_end = config.PUNCH_ACTIVE_FRAMES
        if not active_start <= animation.current_frame <= active_end:
            return None
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

    def is_parry_active(self) -> bool:
        if self.player_state != 'parry':
            return False
        animation = self.player_assets.get_animation('parry')
        active_start, active_end = config.PARRY_ACTIVE_FRAMES
        return active_start <= animation.current_frame <= active_end
    
    def reset_position(self, x):
        print(f"Resetting player to server position x={x}")
        self.player_x = x
    
    def set_state(self, state: str):
        self.player_state = state
    
    def enter_state(self, state: str):
        self.player_state = state
        if state == 'punch':
            self.attack_resolved = False
            self.queued_state = None
        animation = self.player_assets.get_animation(state)
        if animation:
            animation.reset()
    
    def queue_state_after_current(self, state: str):
        self.queued_state = state

    def set_hurt(self, x_pos: int):
        self.hurt_x = x_pos

    def get_hurt_done(self) -> bool:
        return self.hurt_done
    
    def player_reset(self):
        self.hurt_x = None
        self.hurt_done = False
        self.player_state = 'wait'
        self.player_x = (config.WINDOW_WIDTH // 2) - 120
        self.velocity = 0
        self.last_tap_time = {pygame.K_LEFT: 0, pygame.K_RIGHT: 0}
        self._inputs = []
        self.recovery_until = 0
        self.buffered_action = None
        self.attack_resolved = False
        self.parry_hit_registered = False
        self.queued_state = None
        self.player_assets.get_animation('win').reset()
        self.player_assets.get_animation('hurt').reset()
