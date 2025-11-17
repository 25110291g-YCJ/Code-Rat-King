import pygame as pg
from typing import Dict, Optional


class AudioManager:
    """Small audio manager that caches sounds and provides safe play methods.

    Usage:
        am = AudioManager()
        s = am.get('hit', 'assets/sound effect/hit.wav')
        am.play('hit')
    """

    def __init__(self) -> None:
        self._cache: Dict[str, Optional[pg.mixer.Sound]] = {}

    def get(self, name: str, path: str) -> Optional[pg.mixer.Sound]:
        if name in self._cache:
            return self._cache[name]
        try:
            snd = pg.mixer.Sound(path)
            self._cache[name] = snd
            return snd
        except Exception:
            self._cache[name] = None
            return None

    def play(self, name: str, path: str = None, volume: float = 1.0) -> None:
        snd = None
        if name in self._cache:
            snd = self._cache[name]
        elif path:
            snd = self.get(name, path)
        if snd:
            try:
                snd.set_volume(max(0.0, min(1.0, volume)))
                snd.play()
            except Exception:
                pass
