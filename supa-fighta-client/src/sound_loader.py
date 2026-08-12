import config
import pygame
from animations.sound import Sound


class SoundLoader:
    _instance = None
    def __new__(cls, *args, **kwargs):
        # Enforce single instance
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if getattr(self, "_initialized", False):
            return
        self._initialized = True
        self.muted = False
        self.sound = {}
        for name, properties in config.SOUND.items():
            path = properties["path"]
            min_repeat=properties.get("min_repeat_gap_ms", 500)
            self.sound[name] = Sound(name, path, min_repeat)

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = SoundLoader()
        return cls._instance

    def get_sound(self, name: str) -> Sound:
        return self.sound.get(name)

    def set_muted(self, muted: bool):
        self.muted = bool(muted)
        volume = 0 if self.muted else 1
        if self.muted:
            pygame.mixer.stop()
            pygame.mixer.music.pause()
        else:
            pygame.mixer.music.unpause()
        for sound in self.sound.values():
            sound.audio.set_volume(volume)
            sound.reset()
        pygame.mixer.music.set_volume(volume)

    def toggle_mute(self) -> bool:
        self.set_muted(not self.muted)
        return self.muted

    def get_status_text(self) -> str:
        return "Sound Off" if self.muted else "Sound On"

def get_sound_loader() -> SoundLoader:
    return SoundLoader.get_instance()
