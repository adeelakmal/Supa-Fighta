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

SNAPSHOT_INTERVAL = 1 / 60
FIGHT_MESSAGE_SECONDS = 0.7
GAME_OVER_SECONDS = 5
RESULT_ANIMATION_MAX_SECONDS = 3
MATCH_TIMER_WARNING_SECONDS = 5
MATCH_TIMER_CENTER_Y = 65
GAME_FONT_PATH = "assets/determination.ttf"
PLAYER_INDICATOR_COLOR = (255, 214, 64)
PLAYER_INDICATOR_OUTLINE_COLOR = (25, 20, 20)

class GameplayState:
    def __init__(
        self,
        player: Player,
        state_manager,
        countdown_seconds: float = 3.0,
        match_duration_seconds: float = 20.0,
        player_name: str = "Guest",
        opponent_name: str = "Opponent"
    ):
        self.running = True
        self.player = player
        self.state_manager = state_manager
        self.player_name = player_name
        self.opponent_name = opponent_name
        self.countdown_seconds = max(0.0, countdown_seconds)
        self.match_duration_seconds = max(1.0, match_duration_seconds)
        self.countdown_end_time = None
        self.fight_message_end_time = None
        self.match_end_time = None
        self.countdown_number_font = pygame.font.Font(GAME_FONT_PATH, 64)
        self.countdown_fight_font = pygame.font.Font(GAME_FONT_PATH, 52)
        self.match_timer_font = pygame.font.Font(GAME_FONT_PATH, 42)
        self.game_over_message_font = pygame.font.Font(GAME_FONT_PATH, 42)
        self.game_over_countdown_font = pygame.font.Font(GAME_FONT_PATH, 16)
        self.player_name_font = pygame.font.Font(GAME_FONT_PATH, 14)
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
        self._snapshot_sequence = 0
        self._current_time = time.time()
        self._last_sent_player_state = None
        self.game_over = False
        self.show_game_over_overlay = False
        self.final_message = None
        self._overlay_shown_time = None
        self._result_animation_started_time = None
        self._frozen_match_seconds = None
        self.winner = None

    def enter(self):        
        # pygame.mixer.music.load(config.MUSIC["fight"])
        # pygame.mixer.music.play(-1,0,0)
        self.opponent.walk_into_frame()
        now = time.monotonic()
        self.countdown_end_time = now + self.countdown_seconds
        self.fight_message_end_time = self.countdown_end_time + FIGHT_MESSAGE_SECONDS
        self.match_end_time = self.countdown_end_time + self.match_duration_seconds
        self.player.velocity = 0
        self._last_sent_player_state = None
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
            self._reveal_overlay_when_animations_finish()
            if (
                self.show_game_over_overlay
                and self._overlay_shown_time is not None
                and time.monotonic() - self._overlay_shown_time >= GAME_OVER_SECONDS
            ):
                self.state_manager.change_state("lobby")
            return

        if Collision.check_overlap(self.player, self.opponent):
            if self.player.player_state!="idle":
                self.player.speed = config.PLAYER_MOVE_SPEED / 2
                self.opponent.opponent_x=self.player.player_x + 80
            else:
                self.opponent.speed = 1
                self.player.player_x=self.opponent.opponent_x - 80

        else:
            self.player.speed = config.PLAYER_MOVE_SPEED
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

        Collision.check_collision(self.player, self.opponent)
        
        self.opponent.update(self.game_over)
        self.player.update(self.opponent.walking_in or countdown_active, self.game_over)
        if countdown_active:
            self.player._inputs.clear()

        self._current_time = time.time()
        dash_started = (
            self.player.player_state == 'dash'
            and self._last_sent_player_state != 'dash'
        )
        snapshot_due = (
            self._current_time - self._last_snapshot_time >= SNAPSHOT_INTERVAL
        )
        if not countdown_active and (dash_started or snapshot_due):
            snapshot = self._create_state_snapshot()
            self.player.net.send_snapshot(snapshot)
            self._cleanup()
        
    def _handle_game_end(self, server_message):
        self.game_over = True
        self.show_game_over_overlay = False
        self._overlay_shown_time = None
        self._result_animation_started_time = time.monotonic()
        self._frozen_match_seconds = self.get_match_seconds_left()
        self.countdown_end_time = None
        self.fight_message_end_time = None
        self.player.velocity = 0
        self.opponent.velocity = 0
        self.opponent.walking_in = False
        self.opponent.moving_to_target = False
        self.opponent.target_x = None

        winner_id = server_message.get('winner')
        if winner_id is None:
            self.final_message = "DRAW"
            self.winner = None
            self.player.enter_state('idle')
            self.opponent.enter_state('idle')
            self._reveal_game_over_overlay()
        elif winner_id == config.PLAYER_ID:
            self.final_message = "YOU WIN!"
            self.winner = self.player
            if self.player.player_state == 'punch':
                self.player.queue_state_after_current('win')
            elif self.player.player_state != 'win':
                self.player.enter_state('win')
            if self.opponent.opponent_state != 'hurt':
                self.opponent.enter_state('hurt')
        else:
            self.final_message = "YOU LOSE!"
            self.winner = self.opponent
            if self.player.player_state != 'hurt':
                self.player.enter_state('hurt')
            if self.opponent.opponent_state == 'punch':
                self.opponent.queue_state_after_current('win')
            elif self.opponent.opponent_state != 'win':
                # The server can announce the result before its final opponent
                # update arrives. Reconstruct the winning punch so the losing
                # client sees the same complete hit-to-victory sequence.
                self.opponent.enter_state('punch')
                self.opponent.attack_resolved = True
                self.opponent.queue_state_after_current('win')

    def _result_animations_finished(self):
        if self.winner is None:
            return True

        animations = (
            self.player.player_assets.get_animation(self.player.player_state),
            self.opponent.opponent_assets.get_animation(self.opponent.opponent_state)
        )
        return all(animation and animation.is_finished() for animation in animations)

    def _reveal_overlay_when_animations_finish(self):
        animation_wait_expired = (
            self._result_animation_started_time is not None
            and time.monotonic() - self._result_animation_started_time
            >= RESULT_ANIMATION_MAX_SECONDS
        )
        if (
            not self.show_game_over_overlay
            and (
                self._result_animations_finished()
                or animation_wait_expired
            )
        ):
            self._reveal_game_over_overlay()

    def _reveal_game_over_overlay(self):
        if self.show_game_over_overlay:
            return
        self.show_game_over_overlay = True
        self._overlay_shown_time = time.monotonic()
    
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

        message = self.game_over_message_font.render(
            self.final_message,
            True,
            message_color
        )
        message_rect = message.get_rect(
            center=(config.WINDOW_WIDTH // 2, config.WINDOW_HEIGHT // 3)
        )
        surface.blit(message, message_rect)

        seconds_left = GAME_OVER_SECONDS
        if self._overlay_shown_time is not None:
            elapsed = time.monotonic() - self._overlay_shown_time
            seconds_left = max(0, math.ceil(GAME_OVER_SECONDS - elapsed))

        countdown = self.game_over_countdown_font.render(
            f"Returning to lobby in {seconds_left}...",
            True,
            (245, 245, 245)
        )
        countdown_rect = countdown.get_rect(
            center=(config.WINDOW_WIDTH // 2, config.WINDOW_HEIGHT // 2)
        )
        surface.blit(countdown, countdown_rect)

    def get_match_seconds_left(self, now=None):
        if self._frozen_match_seconds is not None:
            return self._frozen_match_seconds
        if self.match_end_time is None:
            return math.ceil(self.match_duration_seconds)

        current_time = time.monotonic() if now is None else now
        return max(0, math.ceil(self.match_end_time - current_time))

    def draw_match_timer(self, surface):
        if self.show_game_over_overlay:
            return
        if not self.game_over and self.is_countdown_active():
            return

        seconds_left = self.get_match_seconds_left()
        timer_color = (
            (245, 80, 80)
            if seconds_left <= MATCH_TIMER_WARNING_SECONDS
            else (245, 245, 245)
        )
        timer_text = self.match_timer_font.render(
            str(seconds_left),
            True,
            timer_color
        )
        timer_rect = timer_text.get_rect(
            center=(config.WINDOW_WIDTH // 2, MATCH_TIMER_CENTER_Y)
        )
        shadow = self.match_timer_font.render(
            str(seconds_left),
            True,
            (25, 20, 20)
        )
        surface.blit(shadow, timer_rect.move(2, 2))
        surface.blit(timer_text, timer_rect)

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

    def draw_player_indicator(self, surface):
        if self.show_game_over_overlay:
            return

        center_x = round(
            self.player.player_x + (config.PLAYER_WIDTH // 2)
        )
        center_x = max(10, min(config.WINDOW_WIDTH - 10, center_x))
        top_y = round(self.player.player_y - 9)

        outline_points = (
            (center_x - 8, top_y),
            (center_x + 8, top_y),
            (center_x, top_y + 11)
        )
        fill_points = (
            (center_x - 5, top_y + 2),
            (center_x + 5, top_y + 2),
            (center_x, top_y + 8)
        )
        pygame.draw.polygon(
            surface,
            PLAYER_INDICATOR_OUTLINE_COLOR,
            outline_points
        )
        pygame.draw.polygon(
            surface,
            PLAYER_INDICATOR_COLOR,
            fill_points
        )
        
    def draw(self, screen: pygame.Surface):
        self.background.draw(screen)
        self.opponent.draw(screen)
        self.player.draw(screen)
        self.draw_player_names(screen)
        self.draw_player_indicator(screen)
        self.draw_match_timer(screen)
        if config.DEBUG:
            Collision.debug_draw(screen, self.player, self.opponent)
        self.draw_countdown(screen)
        if self.show_game_over_overlay:
            self.draw_game_over(screen)

    def _create_state_snapshot(self):
        snapshot = {
            "sequence": self._snapshot_sequence,
            "timestamp": time.time(),
            "player": {
                "x": self.player.player_x,
                "y": self.player.player_y,
                "history": self.player._inputs,
                "state": getattr(self.player, "player_state", "idle")
            }
        }
        self._snapshot_sequence += 1
        return snapshot
    
    def _cleanup(self):
        self._last_sent_player_state = self.player.player_state
        self.player._inputs.clear()
        self._last_snapshot_time = self._current_time
        
    def handle_event(self,event):
        pass
