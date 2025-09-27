import pygame
import config
from typing import Dict
from server.ws_client import WSClient
from game.player import Player
from animations.sprites import SpriteSheet
from animations.animation import Animator

class LobbyState:

    def __init__(self, state_manager, net: WSClient):
        self.state_manager = state_manager
        self.net = net
        self.lobby_state = "Waiting for a game"
        self.font = pygame.font.Font(None, 18)
        self.player = Player((config.WINDOW_WIDTH // 2) - 120, config.WINDOW_HEIGHT - (120 + 20), net)
        self.background_sprites = SpriteSheet("./supa-fighta-client/assets/background.png").get_sprites(config.WINDOW_WIDTH, config.WINDOW_HEIGHT, 1, 8)
        self.background = Animator(self.background_sprites, 10)

    def enter(self):
        self.running = True
    def exit(self):
        self.running = False
     
    def update(self):
        self.background.update()
        self.player.waiting_animation()
        server_message = self.net.get_last_response()
        # self.lobby_state += "." 
        if server_message:
            self.check_for_match(server_message)

    def draw(self, screen):
        self.background.draw(screen)
        self.player.draw(screen)
        lobby_state = self.font.render(self.lobby_state, True, (255, 255, 255))
        rect = lobby_state.get_rect(center=(config.WINDOW_WIDTH - 80, config.WINDOW_HEIGHT - 20))
        screen.blit(lobby_state, rect)

    def handle_event(self, event):
        pass
    
    def check_for_match(self, server_message: Dict):
        if 'match_created' in server_message.get('type') and (server_message.get('player1', None) == config.PLAYER_ID or server_message.get('player2', None) == config.PLAYER_ID):
                self.lobby_state = "Match found! Starting game..."
                pygame.time.delay(1000)
                self.state_manager.change_state("gameplay")