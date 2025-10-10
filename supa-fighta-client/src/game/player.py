from loader import AssetLoader
import pygame

ACTIONABLE_STATES = ['dash', 'punch', 'parry']
DASH_FACTOR = 2.5

class Player:
    def __init__(self, x, y, net):
        self.player_assets = AssetLoader()
        self.last_tap_time = {pygame.K_LEFT: 0, pygame.K_RIGHT: 0}
        self._inputs = []
        self.player_x = x
        self.player_y = y
        self.speed = 2
        self.player_state ='idle'
        self.velocity = 0
        self.rect = pygame.Rect(x, y, 120, 120)
        self.net = net

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
        self._inputs.append(self.player_state)

    def update(self):
        self.player_assets.get_animation(self.player_state).update()
        self.player_x += self.velocity
        self.rect.x = self.player_x
        if self.player_state in ACTIONABLE_STATES:
            if self.player_assets.get_animation(self.player_state).is_finished():
                self.player_state = 'idle'
        else:
            self.handle_keys()
    
    def check_collision(self, other_player):
        if self.rect.colliderect(other_player.rect):
            # Moving right
            if self.velocity > 0:
                self.player_x = other_player.player_x - 120
            # Moving left
            elif self.velocity < 0:
                self.player_x = other_player.player_x + 120
            
            # Update rect position after collision resolution
            self.rect.x = self.player_x
            self.velocity = 0
            return True
        return False

    def draw(self, surface):
        self.player_assets.get_animation(self.player_state).draw(surface, (self.player_x, self.player_y))
    
    def waiting_animation(self):
        self.player_assets.get_animation('idle').update()