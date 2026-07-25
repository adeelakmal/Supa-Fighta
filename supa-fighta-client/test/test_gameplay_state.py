import math
import os
import sys
import types
import unittest
from unittest.mock import patch


PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
SOURCE_ROOT = os.path.join(PROJECT_ROOT, "src")
if SOURCE_ROOT not in sys.path:
    sys.path.insert(0, SOURCE_ROOT)

# These tests exercise state transitions only, so the optional rendering and
# networking packages do not need to be installed in a server-side test run.
try:
    import pygame  # noqa: F401
except ModuleNotFoundError:
    pygame_stub = types.ModuleType("pygame")
    pygame_stub.Rect = type("Rect", (), {})
    pygame_stub.Surface = type("Surface", (), {})
    sys.modules["pygame"] = pygame_stub

try:
    import websocket  # noqa: F401
except ModuleNotFoundError:
    sys.modules["websocket"] = types.ModuleType("websocket")

from game.states.gameplayState import GameplayState


class FakeAnimation:
    def __init__(self, finished=False):
        self.finished = finished
        self.reset_count = 0

    def is_finished(self):
        return self.finished

    def reset(self):
        self.finished = False
        self.reset_count += 1


class FakeAssets:
    def __init__(self):
        self.animations = {
            "idle": FakeAnimation(),
            "hurt": FakeAnimation(),
            "punch": FakeAnimation(),
            "win": FakeAnimation()
        }

    def get_animation(self, state):
        return self.animations.get(state)


class FakePlayer:
    def __init__(self, state="idle"):
        self.player_state = state
        self.player_assets = FakeAssets()
        self.velocity = 1
        self.queued_state = None

    def enter_state(self, state):
        self.player_state = state
        self.player_assets.get_animation(state).reset()

    def queue_state_after_current(self, state):
        self.queued_state = state


class FakeOpponent:
    def __init__(self, state="idle"):
        self.opponent_state = state
        self.opponent_assets = FakeAssets()
        self.velocity = 1
        self.queued_state = None
        self.attack_resolved = False
        self.walking_in = True
        self.moving_to_target = True
        self.target_x = 320

    def enter_state(self, state):
        self.opponent_state = state
        self.opponent_assets.get_animation(state).reset()

    def queue_state_after_current(self, state):
        self.queued_state = state


def make_gameplay_state():
    state = GameplayState.__new__(GameplayState)
    state.player = FakePlayer()
    state.opponent = FakeOpponent()
    state.game_over = False
    state.show_game_over_overlay = False
    state.final_message = None
    state.winner = None
    state._overlay_shown_time = None
    state._result_animation_started_time = None
    state._frozen_match_seconds = None
    state.match_duration_seconds = 20.0
    state.match_end_time = 120.0
    state.countdown_end_time = 100.0
    state.fight_message_end_time = 100.7
    return state


class GameplayStateTests(unittest.TestCase):
    def test_match_timer_uses_deadline_and_clamps_at_zero(self):
        state = make_gameplay_state()

        self.assertEqual(state.get_match_seconds_left(now=100.1), 20)
        self.assertEqual(state.get_match_seconds_left(now=115.2), 5)
        self.assertEqual(state.get_match_seconds_left(now=121.0), 0)

    def test_result_overlay_waits_for_both_animations(self):
        state = make_gameplay_state()
        state.player.player_state = "win"
        state.opponent.opponent_state = "hurt"
        state.winner = state.player
        state._result_animation_started_time = 100.0

        with patch(
            "game.states.gameplayState.time.monotonic",
            return_value=101.0
        ):
            state._reveal_overlay_when_animations_finish()
        self.assertFalse(state.show_game_over_overlay)

        state.player.player_assets.get_animation("win").finished = True
        with patch(
            "game.states.gameplayState.time.monotonic",
            return_value=101.0
        ):
            state._reveal_overlay_when_animations_finish()
        self.assertFalse(state.show_game_over_overlay)

        state.opponent.opponent_assets.get_animation("hurt").finished = True
        with patch(
            "game.states.gameplayState.time.monotonic",
            return_value=250.0
        ):
            state._reveal_overlay_when_animations_finish()

        self.assertTrue(state.show_game_over_overlay)
        self.assertEqual(state._overlay_shown_time, 250.0)

    def test_result_overlay_has_a_maximum_animation_wait(self):
        state = make_gameplay_state()
        state.player.player_state = "win"
        state.opponent.opponent_state = "hurt"
        state.winner = state.player
        state._result_animation_started_time = 100.0

        with patch(
            "game.states.gameplayState.time.monotonic",
            return_value=103.0
        ):
            state._reveal_overlay_when_animations_finish()

        self.assertTrue(state.show_game_over_overlay)
        self.assertEqual(state._overlay_shown_time, 103.0)

    def test_game_end_does_not_restart_an_existing_hurt_animation(self):
        state = make_gameplay_state()
        state.opponent.opponent_state = "hurt"
        state.opponent.opponent_assets.get_animation("hurt").finished = False

        with (
            patch("game.states.gameplayState.config.PLAYER_ID", "winner"),
            patch(
                "game.states.gameplayState.time.monotonic",
                return_value=110.0
            )
        ):
            state._handle_game_end({"winner": "winner"})

        self.assertEqual(state.player.player_state, "win")
        self.assertEqual(
            state.player.player_assets.get_animation("win").reset_count,
            1
        )
        self.assertEqual(state.opponent.opponent_state, "hurt")
        self.assertEqual(
            state.opponent.opponent_assets.get_animation("hurt").reset_count,
            0
        )
        self.assertEqual(state._frozen_match_seconds, math.ceil(120.0 - 110.0))

    def test_winning_punch_finishes_before_victory_animation(self):
        state = make_gameplay_state()
        state.player.player_state = "punch"

        with (
            patch("game.states.gameplayState.config.PLAYER_ID", "winner"),
            patch(
                "game.states.gameplayState.time.monotonic",
                return_value=110.0
            )
        ):
            state._handle_game_end({"winner": "winner"})

        self.assertEqual(state.player.player_state, "punch")
        self.assertEqual(state.player.queued_state, "win")
        self.assertEqual(
            state.player.player_assets.get_animation("win").reset_count,
            0
        )
        self.assertFalse(state.show_game_over_overlay)

    def test_game_end_stops_opponent_intro_movement(self):
        state = make_gameplay_state()
        self.assertTrue(state.opponent.walking_in)

        with (
            patch("game.states.gameplayState.config.PLAYER_ID", "winner"),
            patch(
                "game.states.gameplayState.time.monotonic",
                return_value=110.0
            )
        ):
            state._handle_game_end({
                "winner": "winner",
                "reason": "opponent_disconnected"
            })

        self.assertFalse(state.opponent.walking_in)
        self.assertFalse(state.opponent.moving_to_target)
        self.assertIsNone(state.opponent.target_x)
        self.assertEqual(state.player.player_state, "win")
        self.assertEqual(state.opponent.opponent_state, "hurt")

    def test_loser_sees_opponents_punch_before_victory_animation(self):
        state = make_gameplay_state()
        state.opponent.opponent_state = "idle"

        with (
            patch("game.states.gameplayState.config.PLAYER_ID", "loser"),
            patch(
                "game.states.gameplayState.time.monotonic",
                return_value=110.0
            )
        ):
            state._handle_game_end({"winner": "winner"})

        self.assertEqual(state.player.player_state, "hurt")
        self.assertEqual(state.opponent.opponent_state, "punch")
        self.assertTrue(state.opponent.attack_resolved)
        self.assertEqual(state.opponent.queued_state, "win")
        self.assertEqual(
            state.opponent.opponent_assets.get_animation("win").reset_count,
            0
        )
        self.assertFalse(state.show_game_over_overlay)

    def test_draw_result_reveals_its_overlay_immediately(self):
        state = make_gameplay_state()

        with (
            patch("game.states.gameplayState.config.PLAYER_ID", "player"),
            patch(
                "game.states.gameplayState.time.monotonic",
                return_value=110.0
            )
        ):
            state._handle_game_end({"winner": None})

        self.assertTrue(state.show_game_over_overlay)
        self.assertEqual(state._overlay_shown_time, 110.0)


if __name__ == "__main__":
    unittest.main()
