import pygame as pg
from random import randint
import settings
from settings import *


class Particle(pg.sprite.Sprite):
    """简单的碎片粒子，用于树木破碎特效。"""

    def __init__(self, x: int, y: int, color: tuple) -> None:
        super().__init__()
        size = randint(4, 10)
        self.image = pg.Surface((size, size), pg.SRCALPHA)
        pg.draw.rect(self.image, color, (0, 0, size, size))
        self.rect = self.image.get_rect(center=(x, y))
        # 随机速度
        self.vx = randint(-6, 6)
        self.vy = randint(-10, -3)
        self.life = settings.PARTICLE_LIFETIME

    def update(self) -> None:
        """Per-frame physics update for shard particles: apply gravity and age."""
        # 简单物理：重力加速度
        self.vy += 1
        self.rect.x += self.vx
        self.rect.y += self.vy
        self.life -= 1
        if self.life <= 0:
            self.kill()


class DustParticle(pg.sprite.Sprite):
    """短寿命的着陆尘土粒子，用于落地/跳跃效果。"""

    def __init__(self, x: int, y: int, color: tuple) -> None:
        super().__init__()
        size = randint(getattr(settings, 'DUST_PARTICLE_SIZE_MIN', 4), getattr(settings, 'DUST_PARTICLE_SIZE_MAX', 10))
        self.orig_life = getattr(settings, 'DUST_PARTICLE_LIFETIME', max(6, FPS // 6))
        self.life = self.orig_life
        self.image = pg.Surface((size, size), pg.SRCALPHA)
        try:
            pg.draw.circle(self.image, (*color, 220), (size // 2, size // 2), size // 2)
        except Exception:
            pg.draw.circle(self.image, (200, 180, 140, 220), (size // 2, size // 2), size // 2)
        self.rect = self.image.get_rect(center=(x, y))
        # 初始速度向四周散开，偏向水平
        self.vx = randint(-6, 6)
        self.vy = randint(-8, -2)

    def update(self) -> None:
        """Per-frame update for dust particles: physics + fade-out over life."""
        # 小的重力效果
        self.vy += 1
        self.rect.x += self.vx
        self.rect.y += self.vy
        self.life -= 1
        # 逐渐淡出
        try:
            alpha = int(255 * (self.life / max(1, self.orig_life)))
            self.image.set_alpha(max(0, alpha))
        except Exception:
            pass
        if self.life <= 0:
            self.kill()
