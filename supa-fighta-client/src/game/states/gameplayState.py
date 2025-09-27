from game.player import Player
from game.opponent import Opponent
from server.ws_client import WSClient
import config
import pygame
import time

class GameplayState:
    def __init__(self, net: WSClient):
        self.running = True
        self.net = net
        self.player = Player((config.WINDOW_WIDTH // 2) - 120, config.WINDOW_HEIGHT - (120 + 20), net)
        self.opponent = Opponent(config.WINDOW_WIDTH, config.WINDOW_HEIGHT - (120 + 20), net)
        self.background = pygame.image.load("./supa-fighta-client/assets/background.png").convert()
        self._last_snapshot_time = time.time()
        self._current_time = time.time()

    def enter(self):
        self.opponent.walk_into_frame()
        self.running = True
    def exit(self):
        self.running = False
    def update(self):
        self.opponent.update()
        self.player.update()
        self._current_time = time.time()
        if self._current_time - self._last_snapshot_time >= 0.1:
            snapshot = self._create_state_snapshot()
            self.net.send_snapshot(snapshot)
            self._cleanup()
        
    def draw(self, screen: pygame.Surface):
        screen.blit(self.background, (0, 0))
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