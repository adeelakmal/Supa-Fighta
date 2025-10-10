from game.player import Player
from server.ws_client import WSClient
import config
import pygame
import time

class GameplayState:
    def __init__(self, net: WSClient):
        self.running = True
        self.net = net
        self.player = Player(config.WINDOW_WIDTH // 2, config.WINDOW_HEIGHT // 2, net)
        self.background = pygame.image.load("./supa-fighta-client/assets/background.png").convert()
        self._last_snapshot_time = time.time()
        self._current_time = time.time()

    def enter(self):
        self.running = True
    def exit(self):
        self.running = False
    def update(self):
        self.player.update()
        self._current_time = time.time()
        if self._current_time - self._last_snapshot_time >= 0.1:
            snapshot = self._create_state_snapshot()
            self.net.send_snapshot(snapshot)
            self._cleanup()
        if self.player1.check_collision(self.player2):
            print("Collision detected!")
        
    def draw(self, screen: pygame.Surface):
        screen.blit(self.background, (0, 0))
        self.player.draw(screen)

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