import pygame

import config


class GameDisplay:
    """Render a fixed logical canvas to an integer-scaled game window."""

    def __init__(self, resolution=config.DEFAULT_DISPLAY_RESOLUTION):
        self._resolution = None
        self._screen = None
        self._logical_surface = pygame.Surface(config.LOGICAL_SIZE)
        self.set_resolution(resolution)

    @property
    def logical_surface(self):
        return self._logical_surface

    @property
    def resolution(self):
        return self._resolution

    def set_resolution(self, resolution):
        resolution = tuple(resolution)
        if resolution not in config.DISPLAY_RESOLUTIONS:
            raise ValueError(f"Unsupported display resolution: {resolution}")

        self._screen = pygame.display.set_mode(resolution)
        self._resolution = resolution
        return self._resolution

    def cycle_resolution(self, direction=1):
        current_index = config.DISPLAY_RESOLUTIONS.index(self._resolution)
        next_index = (
            current_index + direction
        ) % len(config.DISPLAY_RESOLUTIONS)
        return self.set_resolution(config.DISPLAY_RESOLUTIONS[next_index])

    def to_logical_event(self, event):
        """Return mouse events with positions mapped to logical coordinates."""
        if not hasattr(event, "pos"):
            return event

        display_width, display_height = self._resolution
        logical_width, logical_height = config.LOGICAL_SIZE
        physical_x, physical_y = event.pos
        logical_pos = (
            max(
                0,
                min(
                    logical_width - 1,
                    physical_x * logical_width // display_width,
                ),
            ),
            max(
                0,
                min(
                    logical_height - 1,
                    physical_y * logical_height // display_height,
                ),
            ),
        )

        attributes = event.dict.copy()
        attributes["pos"] = logical_pos
        if "rel" in attributes:
            relative_x, relative_y = attributes["rel"]
            attributes["rel"] = (
                round(relative_x * logical_width / display_width),
                round(relative_y * logical_height / display_height),
            )
        return pygame.event.Event(event.type, attributes)

    def present(self):
        """Nearest-neighbor scale the logical frame and show it."""
        if self._resolution == config.LOGICAL_SIZE:
            self._screen.blit(self._logical_surface, (0, 0))
        else:
            pygame.transform.scale(
                self._logical_surface,
                self._resolution,
                self._screen,
            )
        pygame.display.flip()
