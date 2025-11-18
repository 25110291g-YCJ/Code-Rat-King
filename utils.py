from typing import Tuple


def clamp(v: float, lo: float, hi: float) -> float:
    """Clamp a value v to the inclusive range [lo, hi]."""
    return max(lo, min(hi, v))


def lerp(a: float, b: float, t: float) -> float:
    """Linearly interpolate between a and b by parameter t (clamped 0..1)."""
    return a + (b - a) * clamp(t, 0.0, 1.0)


def center_rect_for(surface_w: int, surface_h: int, w: int, h: int) -> Tuple[int, int]:
    """Return top-left coordinates to center a w*h rect inside surface_w*surface_h."""
    x = (surface_w - w) // 2
    y = (surface_h - h) // 2
    return x, y
