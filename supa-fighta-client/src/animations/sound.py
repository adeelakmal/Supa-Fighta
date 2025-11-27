import pygame

class Sound:
    def __init__(self, name, path, min_repeat_gap_ms: int = 500):
        self.name = name
        self.path = path
        self.audio = pygame.mixer.Sound(path)
        self._channel = None
        self._played = False
        self._last_play_ms = 0
        self._min_repeat_gap_ms = int(min_repeat_gap_ms)

    def play(self, force: bool = False):
        now = pygame.time.get_ticks()
        # If caller explicitly forces a play, bypass guards
        if force:
            self._channel = self.audio.play()
            self._played = True
            self._last_play_ms = now
            return self._channel
        # If we haven't played yet during this activation -> play and lock
        if not self._played:
            self._channel = self.audio.play()
            self._played = True
            self._last_play_ms = now
            return self._channel

        # We already played during this activation. If sound is still playing,
        # don't restart it.
        if self._channel is not None and self._channel.get_busy():
            return self._channel

        # If the cooldown has expired we allow the sound to be played again.
        if now - self._last_play_ms > self._min_repeat_gap_ms:
            self._channel = self.audio.play()
            self._last_play_ms = now
            return self._channel

        return None

    def reset(self):
        self._played = False
        self._last_play_ms = 0

    def is_playing(self) -> bool:
        return bool(self._channel and self._channel.get_busy())