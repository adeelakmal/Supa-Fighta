import pygame
import config
from typing import Dict
from server.ws_client import WSClient
from game.player import Player
from animations.sprites import SpriteSheet
from animations.animation import Animator
from type.sprite import SpriteProperties
from sound_loader import SoundLoader

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
        self.match_countdown_seconds = 3.0
        self.player_name = "Guest"
        self.opponent_name = "Opponent"
        self.background = Animator(self.background_sprites, 10)
        self.sound_loader = SoundLoader.get_instance()

    def enter(self):
        self.running = True
        if self.player is None:
            try:
                self.player = Player(
                    (config.WINDOW_WIDTH // 2) - 120,
                    config.WINDOW_HEIGHT - (120 + 20)
                )
            except ConnectionError as error:
                print(f"Could not connect to the server: {error}")
                self.state_manager.show_connection_error(str(error))
        else:
            self.player.player_reset()
            self.send_player_rejoined()

    def exit(self):
        self.running = False
     
    def update(self):
        self.background.update()
        if self.player is None:
            return

        connection_error = self.player.net.get_connection_error()
        if connection_error:
            self.state_manager.show_connection_error(connection_error)
            return

        name_rejected = self.player.net.get_name_rejected_message()
        if name_rejected:
            message = str(
                name_rejected.get('message')
                or "Please choose another player name."
            )
            self.state_manager.show_name_error(message)
            return

        self.player.waiting_animation()
        # The network keeps this safe until the lobby reads it here.
        match_message = self.player.net.get_match_created_message()
        if match_message:
            self.check_for_match(match_message)

    def draw(self, screen):
        self.background.draw(screen)
        self.player.draw(screen)
        lobby_state = self.font.render(self.lobby_state, True, (255, 255, 255))
        rect = lobby_state.get_rect(center=(config.WINDOW_WIDTH - 80, config.WINDOW_HEIGHT - 20))
        screen.blit(lobby_state, rect)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.sound_loader.get_sound("button_select").play()
            self.disconnect_player()
            self.state_manager.change_state("main_menu")

    def get_player(self):
        return self.player

    def get_match_countdown_seconds(self):
        return self.match_countdown_seconds

    def get_match_player_names(self):
        return self.player_name, self.opponent_name
    
    def check_for_match(self, server_message: Dict):
        if server_message.get('type') == 'match_created' and (
            server_message.get('player1') == config.PLAYER_ID
            or server_message.get('player2') == config.PLAYER_ID
        ):
                if server_message.get('player1') == config.PLAYER_ID:
                    self.player_name = server_message.get('player1Name', 'Guest')
                    self.opponent_name = server_message.get('player2Name', 'Opponent')
                else:
                    self.player_name = server_message.get('player2Name', 'Guest')
                    self.opponent_name = server_message.get('player1Name', 'Opponent')

                starts_at = server_message.get('startsAt')
                server_time = server_message.get('serverTime')

                if isinstance(starts_at, (int, float)) and isinstance(server_time, (int, float)):
                    remaining_ms = max(0, starts_at - server_time)
                    self.match_countdown_seconds = min(10.0, remaining_ms / 1000)
                else:
                    countdown = server_message.get('countdownSeconds', 3)
                    try:
                        self.match_countdown_seconds = min(10.0, max(0.0, float(countdown)))
                    except (TypeError, ValueError):
                        self.match_countdown_seconds = 3.0

                self.state_manager.change_state("gameplay")

    def send_player_rejoined(self):
        if self.player:
            self.player.net.send({
                "type": "player_rejoined"
            })

    def disconnect_player(self):
        if self.player and self.player.net:
            self.player.net.close()
        self.player = None
