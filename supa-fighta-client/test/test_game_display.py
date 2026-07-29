import os
import sys
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


class GameDisplayTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def setUp(self):
        self.display = GameDisplay()

    def test_supported_resolutions_are_integer_scales(self):
        self.assertEqual(
            config.DISPLAY_RESOLUTIONS,
            ((640, 360), (1280, 720), (1920, 1080)),
        )
        for scale, resolution in enumerate(
            config.DISPLAY_RESOLUTIONS,
            start=1,
        ):
            self.assertEqual(
                resolution,
                (
                    config.WINDOW_WIDTH * scale,
                    config.WINDOW_HEIGHT * scale,
                ),
            )

    def test_resolution_changes_keep_logical_canvas_fixed(self):
        logical_surface = self.display.logical_surface
        for resolution in config.DISPLAY_RESOLUTIONS:
            self.display.set_resolution(resolution)
            self.assertEqual(self.display.resolution, resolution)
            self.assertIs(self.display.logical_surface, logical_surface)
            self.assertEqual(logical_surface.get_size(), (640, 360))

    def test_mouse_positions_map_to_logical_coordinates(self):
        self.display.set_resolution((1920, 1080))
        event = pygame.event.Event(
            pygame.MOUSEMOTION,
            pos=(300, 150),
            rel=(6, 3),
            buttons=(False, False, False),
        )
        logical_event = self.display.to_logical_event(event)
        self.assertEqual(logical_event.pos, (100, 50))
        self.assertEqual(logical_event.rel, (2, 1))

    def test_present_creates_nearest_neighbor_pixel_blocks(self):
        canvas = self.display.logical_surface
        canvas.fill((0, 0, 0))
        canvas.set_at((0, 0), (255, 0, 0))
        canvas.set_at((1, 0), (0, 255, 0))

        for scale, resolution in ((2, (1280, 720)), (3, (1920, 1080))):
            self.display.set_resolution(resolution)
            self.display.present()
            screen = pygame.display.get_surface()
            for x in range(scale):
                for y in range(scale):
                    self.assertEqual(
                        screen.get_at((x, y))[:3],
                        (255, 0, 0),
                    )
            self.assertEqual(
                screen.get_at((scale, 0))[:3],
                (0, 255, 0),
            )


class ResolutionSettingsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def setUp(self):
        self.display = GameDisplay()
        self.game_state = GameState(self.display)
        self.game_state.change_state("settings")
        self.settings = self.game_state.current_state()

    def test_resolution_button_opens_preset_submenu(self):
        self.settings._activate("Resolution")
        submenu = self.game_state.current_state()

        self.assertEqual(type(submenu).__name__, "ResolutionMenuState")
        self.assertEqual(
            [button.text for button in submenu.buttons],
            ["640x360", "1280x720", "1920x1080"],
        )
        self.assertFalse(hasattr(submenu, "textfield"))
        for button in submenu.buttons:
            self.assertEqual(button.rect.centerx, config.WINDOW_WIDTH // 2)
            self.assertEqual(
                button.rect.size,
                submenu.PRESET_BUTTON_SIZE,
            )
        self.assertEqual(submenu.PRESET_FONT_SIZE, 16)
        self.assertEqual(submenu.selected_button.font_color, (92, 45, 28))
        self.assertEqual(submenu.TITLE_FONT_SIZE, 40)
        self.assertEqual(submenu.TITLE_CENTER_Y_OFFSET, 34)
        self.assertEqual(
            [
                submenu.buttons[index + 1].rect.y
                - submenu.buttons[index].rect.y
                for index in range(len(submenu.buttons) - 1)
            ],
            [submenu.PRESET_SPACING, submenu.PRESET_SPACING],
        )
        self.assertEqual(submenu.PRESET_SPACING, 24)

    def test_resolution_submenu_applies_preset_and_closes(self):
        self.settings._activate("Resolution")
        submenu = self.game_state.current_state()

        submenu._activate("1920x1080")

        self.assertEqual(self.display.resolution, (1920, 1080))
        self.assertIs(self.game_state.current_state(), self.settings)

    def test_settings_has_only_three_options(self):
        self.assertEqual(
            [button.text for button in self.settings.buttons],
            ["Player Name", "Sound", "Resolution"],
        )
        self.assertEqual(
            self.settings.buttons[2].font.size("Resolution"),
            self.settings.buttons[0].font.size("Resolution"),
        )

    def test_settings_uses_main_menu_button_coordinates(self):
        self.assertEqual(
            [button.rect.topleft for button in self.settings.buttons],
            [(16, 170), (16, 210), (16, 250)],
        )

    def test_settings_draws_at_every_resolution(self):
        canvas = self.display.logical_surface
        self.settings._activate("Resolution")
        for resolution in config.DISPLAY_RESOLUTIONS:
            self.display.set_resolution(resolution)
            self.game_state.draw(canvas)
            self.display.present()
            self.assertEqual(canvas.get_size(), config.LOGICAL_SIZE)


if __name__ == "__main__":
    unittest.main()
