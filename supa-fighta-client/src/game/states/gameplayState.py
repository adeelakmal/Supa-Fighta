from game.player import Player
from game.opponent import Opponent
from server.ws_client import WSClient
from animations.sprites import SpriteSheet
from animations.animation import Animator
import config
import pygame
import time

class GameplayState:
    def __init__(self, player: Player):
        self.running = True
        self.player = player
        if player is None: # for testing purposes
            self.player = Player((config.WINDOW_WIDTH // 2) - 120, config.WINDOW_HEIGHT - (120 + 20))
        self.opponent = Opponent(config.WINDOW_WIDTH, config.WINDOW_HEIGHT - (120 + 20))
        self.background_sprites = SpriteSheet("./supa-fighta-client/assets/background.png").get_sprites(config.WINDOW_WIDTH, config.WINDOW_HEIGHT, 1, 8)
        self.background = Animator(self.background_sprites, 10)
        self._last_snapshot_time = time.time()
        self._current_time = time.time()

    def enter(self):
        self.opponent.walk_into_frame()
        self.running = True
    def exit(self):
        self.running = False
    def update(self):
        self.background.update()
        self.opponent.update()
        self.player.update()
        self._current_time = time.time()
        if self._current_time - self._last_snapshot_time >= 0.1:
            snapshot = self._create_state_snapshot()
            self.player.net.send_snapshot(snapshot)
            self._cleanup()
        
    def draw(self, screen: pygame.Surface):
        self.background.draw(screen)
        self.player.draw(screen)
        self.opponent.draw(screen)

    def _create_state_snapshot(self):
        snapshot = {
            "timestamp": time.time(),
            "player": {
                "x": self.player.player_x,
                "y": self.player.player_y,
                "history": self.player._inputs,
                "state": getattr(self.player, "player_state", "idel")
            }
        }
        return snapshot
    
    def _cleanup(self):
        self.player._inputs.clear()
        self._last_snapshot_time = self._current_time
        
    def handle_event(self,event):
        pass