import pygame
import config
from typing import Dict
from server.ws_client import WSClient
from game.player import Player
from animations.sprites import SpriteSheet
from animations.animation import Animator
from type.sprite import SpriteProperties

class LobbyState:

    def __init__(self, state_manager):
        self.state_manager = state_manager
        self.lobby_state = "Waiting for a game..."
        self.font = pygame.font.Font(None, 18)
        self.background_sprites = SpriteSheet(
            SpriteProperties(
                path="assets/background.png",
                width=config.WINDOW_WIDTH,
                height=config.WINDOW_HEIGHT,
                rows=1,
                cols=8,
            )
        )
        self.player = None
        self.background = Animator(self.background_sprites, 10)

    def enter(self):
        self.running = True
        if self.player is None:
            self.player = Player((config.WINDOW_WIDTH // 2) - 120, config.WINDOW_HEIGHT - (120 + 20))
        else:
            self.send_player_rejoined()

    def exit(self):
        self.running = False
     
    def update(self):
        self.background.update()
        self.player.waiting_animation()
        server_message = self.player.net.get_last_response()
        if server_message:
            self.check_for_match(server_message)

    def draw(self, screen):
        self.background.draw(screen)
        self.player.draw(screen)
        lobby_state = self.font.render(self.lobby_state, True, (255, 255, 255))
        rect = lobby_state.get_rect(center=(config.WINDOW_WIDTH - 80, config.WINDOW_HEIGHT - 20))
        screen.blit(lobby_state, rect)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.state_manager.change_state("main_menu")

    def get_player(self):
        return self.player
    
    def check_for_match(self, server_message: Dict):
        if 'match_created' in server_message.get('type') and (server_message.get('player1', None) == config.PLAYER_ID or server_message.get('player2', None) == config.PLAYER_ID):
                self.state_manager.change_state("gameplay")

    def send_player_rejoined(self):
        if self.player:
            self.player.net.send({
                "type": "player_rejoined"
            })