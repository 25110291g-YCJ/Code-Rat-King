import os
import pygame as pg
from typing import Optional, Tuple


def load_image(path: str, size: Optional[Tuple[int, int]] = None, convert_alpha: bool = True) -> pg.Surface:
    """Load an image with graceful fallbacks.

    Args:
        path: relative path to image file
        size: optional (w, h) to scale to
        convert_alpha: whether to use convert_alpha()

    Returns:
        pygame.Surface (possibly a placeholder surface on error)
    """
    try:
        surf = pg.image.load(path)
        if convert_alpha:
            surf = surf.convert_alpha()
        else:
            surf = surf.convert()
        if size:
            surf = pg.transform.scale(surf, size)
        return surf
    except Exception:
        # Create a placeholder surface when loading fails
        w, h = size if size else (64, 64)
        s = pg.Surface((w, h), pg.SRCALPHA)
        s.fill((200, 50, 50, 180))
        try:
            pg.draw.rect(s, (0, 0, 0), s.get_rect(), 2)
        except Exception:
            pass
        return s


def load_sound(path: str) -> Optional[pg.mixer.Sound]:
    """Load a sound and return a Sound or None on failure."""
    try:
        return pg.mixer.Sound(path)
    except Exception:
        return None


def list_pngs(dirpath: str):
    """Return sorted list of png files under dirpath (relative)."""
    try:
        abspath = os.path.abspath(dirpath)
        files = [os.path.join(abspath, f) for f in os.listdir(abspath) if f.lower().endswith('.png')]
        files.sort()
        return files
    except Exception:
        return []
