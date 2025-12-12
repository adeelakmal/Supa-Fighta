from game.player import Player
from game.opponent import Opponent
from animations.sprites import SpriteSheet
from type.sprite import SpriteProperties
from animations.animation import Animator
from game.collision import Collision
from server.ws_client import WSClient
import config
import pygame
import time

class GameplayState:
    def __init__(self, player: Player):
        self.running = True
        self.player = player
        # self.net = WSClient(config.WS_URL)
        if player is None: # for testing purposes
            self.player = Player((config.WINDOW_WIDTH // 2) - 120, config.WINDOW_HEIGHT - (120 + 20))
        self.opponent = Opponent(config.WINDOW_WIDTH, config.WINDOW_HEIGHT - (120 + 20))
        self.background_sprites = SpriteSheet(
            SpriteProperties(
                path="./supa-fighta-client/assets/background.png",
                width=config.WINDOW_WIDTH,
                height=config.WINDOW_HEIGHT,
                rows=1,
                cols=8,
            )
        )
        self.background = Animator(self.background_sprites, 10)
        self._last_snapshot_time = time.time()
        self._current_time = time.time()

    def enter(self):        
        pygame.mixer.music.load(config.MUSIC["fight"])
        pygame.mixer.music.play(-1,0,0)
        self.opponent.walk_into_frame()
        self.running = True
    def exit(self):
        self.running = False
    def update(self):
        self.background.update()

        if Collision.check_overlap(self.player, self.opponent):
            if self.player.player_state!="idle":
                self.player.speed = 1
                self.opponent.opponent_x=self.player.player_x + 80
            else:
                self.opponent.speed = 1
                self.player.player_x=self.opponent.opponent_x - 80

        else:
            self.player.speed = 2
            self.opponent.speed = 2

        self.opponent.update()
        self.player.update()     

        # TODO: show victory screen and go back to lobby
        Collision.check_collision(self.player, self.opponent)
        
        self._current_time = time.time()
        if self._current_time - self._last_snapshot_time >= 0.1:
            snapshot = self._create_state_snapshot()
            self.player.net.send_snapshot(snapshot)
            self._cleanup()
        last_opponent_update = self.player.net.get_last_opponent_update()
        if last_opponent_update and not self.opponent.walking_in:
            opp_state = last_opponent_update.get("current_state", "idle")
            opp_position = last_opponent_update.get("position").get("x", self.opponent.opponent_x)
            self.opponent.handle_event(opp_state)
            self.opponent.reset_position(opp_position, self.player.speed) #using player speed to judge if the opponent is being pushed
        last_player_correction = self.player.net.get_last_player_correction()
        if last_player_correction:
            # print(f"Applying correction to player position: {last_player_correction}")
            self.player.reset_position(last_player_correction)
        
    def draw(self, screen: pygame.Surface):
        self.background.draw(screen)
        self.opponent.draw(screen)
        self.player.draw(screen)
        if config.DEBUG:
            Collision.debug_draw(screen, self.player, self.opponent)

    def _create_state_snapshot(self):
        snapshot = {
            "timestamp": time.time(),
            "player": {
                "x": self.player.player_x,
                "y": self.player.player_y,
                "history": self.player._inputs,
                "state": getattr(self.player, "player_state", "idle")
            }
        }
        return snapshot
    
    def _cleanup(self):
        self.player._inputs.clear()
        self._last_snapshot_time = self._current_time
        
    def handle_event(self,event):
        pass