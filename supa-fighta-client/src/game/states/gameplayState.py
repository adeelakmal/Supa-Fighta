from game.player import Player
from game.opponent import Opponent
from animations.sprites import SpriteSheet
from type.sprite import SpriteProperties
from animations.animation import Animator
from game.collision import Collision
from server.ws_client import WSClient
import config
import math
import pygame
import time

SNAPSHOT_INTERVAL = 1 / 30
FIGHT_MESSAGE_SECONDS = 0.7
GAME_OVER_SECONDS = 5

class GameplayState:
    def __init__(
        self,
        player: Player,
        state_manager,
        countdown_seconds: float = 3.0,
        player_name: str = "Guest",
        opponent_name: str = "Opponent"
    ):
        self.running = True
        self.player = player
        self.state_manager = state_manager
        self.player_name = player_name
        self.opponent_name = opponent_name
        self.countdown_seconds = max(0.0, countdown_seconds)
        self.countdown_end_time = None
        self.fight_message_end_time = None
        self.countdown_number_font = pygame.font.SysFont(None, 96, bold=True)
        self.countdown_fight_font = pygame.font.SysFont(None, 82, bold=True)
        self.player_name_font = pygame.font.Font("assets/determination.ttf", 14)
        # self.net = WSClient(config.WS_URL)
        if player is None: # for testing purposes
            self.player = Player((config.WINDOW_WIDTH // 2) - 120, config.WINDOW_HEIGHT - (120 + 20))
        self.opponent = Opponent(config.WINDOW_WIDTH, config.WINDOW_HEIGHT - (120 + 20))
        self.background_sprites = SpriteSheet(
            SpriteProperties(
                path="assets/background.png",
                width=config.WINDOW_WIDTH,
                height=config.WINDOW_HEIGHT,
                rows=1,
                cols=8,
            )
        )
        self.background = Animator(self.background_sprites, 10)
        self._last_snapshot_time = time.time()
        self._current_time = time.time()
        self.game_over = False
        self.final_message = None
        self._game_end_time = None
        self.winner = None

    def enter(self):        
        # pygame.mixer.music.load(config.MUSIC["fight"])
        # pygame.mixer.music.play(-1,0,0)
        self.opponent.walk_into_frame()
        now = time.monotonic()
        self.countdown_end_time = now + self.countdown_seconds
        self.fight_message_end_time = self.countdown_end_time + FIGHT_MESSAGE_SECONDS
        self.player.velocity = 0
        self.running = True

    def exit(self):
        self.running = False
        self.player.player_reset()
        self.opponent.opponent_reset()

    def update(self):
        self.background.update()
        if not self.game_over:
            connection_error = self.player.net.get_connection_error()
            if connection_error:
                self.state_manager.show_connection_error(connection_error)
                return

        countdown_active = self.is_countdown_active()
        if countdown_active:
            self.player.velocity = 0

        if self.player.player_state == 'wait':
            self.player.player_state = 'idle'
        server_message = self.player.net.get_game_end_message()
        if server_message and not self.game_over:
            self._handle_game_end(server_message)

        if self.game_over:
            self.opponent.update(True)
            self.player.update(False, True)
            if (
                self._game_end_time is not None
                and time.monotonic() - self._game_end_time >= GAME_OVER_SECONDS
            ):
                self.state_manager.change_state("lobby")
            return

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
        
        # temp repositioning  
        last_opponent_update = self.player.net.get_last_opponent_update()
        if last_opponent_update and not self.opponent.walking_in and not self.game_over:
            opp_state = last_opponent_update.get("current_state", "idle")
            opp_position = last_opponent_update.get("position").get("x", self.opponent.opponent_x)
            if opp_state == "parried" and self.player.player_state == "parry":
                self.player.enter_state("parry-hit")
            self.opponent.reset_position(opp_position, opp_state) #using player speed to judge if the opponent is being pushed
        last_player_correction = self.player.net.get_last_player_correction()
        if last_player_correction is not None and not self.game_over:
            # print(f"Applying correction to player position: {last_player_correction}")
            self.player.reset_position(last_player_correction)

        # TODO: show victory screen and go back to lobby
        Collision.check_collision(self.player, self.opponent)
        
        self.opponent.update(self.game_over)
        self.player.update(self.opponent.walking_in or countdown_active, self.game_over)
        if countdown_active:
            self.player._inputs.clear()


        if self.player.get_hurt_done() and self.player.player_assets.get_animation('hurt').is_finished():
            self.opponent.set_state('win')
        if self.opponent.get_hurt_done() and self.opponent.opponent_assets.get_animation('hurt').is_finished():
            self.player.set_state('win')
        
        self._current_time = time.time()
        if not countdown_active and self._current_time - self._last_snapshot_time >= SNAPSHOT_INTERVAL:
            snapshot = self._create_state_snapshot()
            self.player.net.send_snapshot(snapshot)
            self._cleanup()
        
    def _handle_game_end(self, server_message):
        self.game_over = True
        self._game_end_time = time.monotonic()
        self.countdown_end_time = None
        self.fight_message_end_time = None
        self.player.velocity = 0
        self.opponent.velocity = 0

        winner_id = server_message.get('winner')
        if winner_id is None:
            self.final_message = "DRAW"
            self.winner = None
            self.player.enter_state('idle')
            self.opponent.enter_state('idle')
        elif winner_id == config.PLAYER_ID:
            self.final_message = "YOU WIN!"
            self.winner = self.player
            self.player.enter_state('win')
            self.opponent.enter_state('hurt')
        else:
            self.final_message = "YOU LOSE!"
            self.winner = self.opponent
            self.player.enter_state('hurt')
            self.opponent.enter_state('win')
    
    def draw_game_over(self, surface):
        overlay = pygame.Surface(
            (config.WINDOW_WIDTH, config.WINDOW_HEIGHT),
            pygame.SRCALPHA
        )
        overlay.fill((0, 0, 0, 150))
        surface.blit(overlay, (0, 0))

        if self.final_message == "YOU WIN!":
            message_color = (80, 230, 120)
        elif self.final_message == "YOU LOSE!":
            message_color = (245, 80, 80)
        else:
            message_color = (255, 214, 64)

        message_font = pygame.font.SysFont(None, 74, bold=True)
        message = message_font.render(self.final_message, True, message_color)
        message_rect = message.get_rect(
            center=(config.WINDOW_WIDTH // 2, config.WINDOW_HEIGHT // 3)
        )
        surface.blit(message, message_rect)

        seconds_left = GAME_OVER_SECONDS
        if self._game_end_time is not None:
            elapsed = time.monotonic() - self._game_end_time
            seconds_left = max(0, math.ceil(GAME_OVER_SECONDS - elapsed))

        countdown_font = pygame.font.SysFont(None, 30)
        countdown = countdown_font.render(
            f"Returning to lobby in {seconds_left}...",
            True,
            (245, 245, 245)
        )
        countdown_rect = countdown.get_rect(
            center=(config.WINDOW_WIDTH // 2, config.WINDOW_HEIGHT // 2)
        )
        surface.blit(countdown, countdown_rect)

    def is_countdown_active(self):
        return (
            self.countdown_end_time is not None
            and time.monotonic() < self.countdown_end_time
        )

    def get_countdown_text(self):
        if self.countdown_end_time is None:
            return None

        now = time.monotonic()
        remaining = self.countdown_end_time - now
        if remaining > 0:
            return str(math.ceil(remaining))
        if now < self.fight_message_end_time:
            return "FIGHT!"
        return None

    def draw_countdown(self, surface):
        countdown_text = self.get_countdown_text()
        if countdown_text is None:
            return

        font = (
            self.countdown_fight_font
            if countdown_text == "FIGHT!"
            else self.countdown_number_font
        )
        shadow = font.render(countdown_text, True, (25, 20, 20))
        text = font.render(countdown_text, True, (255, 214, 64))
        center = (config.WINDOW_WIDTH // 2, config.WINDOW_HEIGHT // 3)
        shadow_rect = shadow.get_rect(center=(center[0] + 3, center[1] + 3))
        text_rect = text.get_rect(center=center)
        surface.blit(shadow, shadow_rect)
        surface.blit(text, text_rect)

    def draw_player_names(self, surface):
        name_y = self.player.player_y - 18
        player_center_x = self.player.player_x + (config.PLAYER_WIDTH // 2)
        opponent_center_x = self.opponent.opponent_x + (config.PLAYER_WIDTH // 2)

        for name, center_x in (
            (self.player_name, player_center_x),
            (self.opponent_name, opponent_center_x)
        ):
            shadow = self.player_name_font.render(name, True, (25, 20, 20))
            text = self.player_name_font.render(name, True, (255, 255, 255))
            text_rect = text.get_rect(center=(center_x, name_y))
            text_rect.clamp_ip(surface.get_rect())
            shadow_rect = text_rect.move(1, 1)
            surface.blit(shadow, shadow_rect)
            surface.blit(text, text_rect)
        
    def draw(self, screen: pygame.Surface):
        self.background.draw(screen)
        self.opponent.draw(screen)
        self.player.draw(screen)
        self.draw_player_names(screen)
        if config.DEBUG:
            Collision.debug_draw(screen, self.player, self.opponent)
        self.draw_countdown(screen)
        if self.game_over:    
            self.draw_game_over(screen)

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
