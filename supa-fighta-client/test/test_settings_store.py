import json
import os
import sys
import tempfile
import unittest
from pathlib import Path


os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")

CLIENT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = CLIENT_ROOT / "src"
sys.path.insert(0, str(SRC_ROOT))

import pygame

import config
from game.stateManager import GameState
from game_display import GameDisplay
from settings_store import load_display_resolution, save_display_resolution


class SettingsStoreTests(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.settings_path = (
            Path(self.temporary_directory.name) / "settings.json"
        )

    def tearDown(self):
        self.temporary_directory.cleanup()

    def test_missing_settings_use_default_resolution(self):
        self.assertEqual(
            load_display_resolution(self.settings_path),
            config.DEFAULT_DISPLAY_RESOLUTION,
        )

    def test_saved_resolution_is_loaded_next_time(self):
        self.assertTrue(
            save_display_resolution((1920, 1080), self.settings_path)
        )
        self.assertEqual(
            load_display_resolution(self.settings_path),
            (1920, 1080),
        )
        with self.settings_path.open("r", encoding="utf-8") as settings_file:
            self.assertEqual(
                json.load(settings_file)["display_resolution"],
                [1920, 1080],
            )

    def test_corrupt_or_unsupported_settings_use_default_resolution(self):
        self.settings_path.write_text("not json", encoding="utf-8")
        self.assertEqual(
            load_display_resolution(self.settings_path),
            config.DEFAULT_DISPLAY_RESOLUTION,
        )

        self.settings_path.write_text(
            json.dumps({"display_resolution": [800, 600]}),
            encoding="utf-8",
        )
        self.assertEqual(
            load_display_resolution(self.settings_path),
            config.DEFAULT_DISPLAY_RESOLUTION,
        )


class ResolutionPersistenceIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def test_applied_resolution_invokes_persistence_callback(self):
        saved_resolutions = []
        display = GameDisplay()
        game_state = GameState(display, saved_resolutions.append)
        game_state.change_state("settings")
        settings = game_state.current_state()

        settings._activate("Resolution")
        game_state.current_state()._activate("1280x720")

        self.assertEqual(saved_resolutions, [(1280, 720)])
        self.assertEqual(display.resolution, (1280, 720))


if __name__ == "__main__":
    unittest.main()
