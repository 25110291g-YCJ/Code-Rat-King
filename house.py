import pygame as pg

import settings
from settings import *


class House(pg.sprite.Sprite):
    """终点房屋，猫碰到后视为通关。"""

    def __init__(self) -> None:
        super().__init__()
        house_image = pg.image.load(HOUSE).convert_alpha()
        self.image = pg.transform.scale(house_image, (HOUSE_WIDTH, HOUSE_HEIGHT))
        self.rect = self.image.get_rect(
            midbottom=(WIDTH + HOUSE_WIDTH, GROUND_HEIGHT + HOUSE_GROUND_OFFSET)
        )

    def animation(self) -> None:
        # 房屋作为终点也随障碍物速度加速
        speed = settings.CURRENT_MOVING_SPEED * getattr(settings, 'OBSTACLE_SPEED_MULTIPLIER', 1.0)
        self.rect.x -= speed

    def update(self) -> None:
        self.animation()
        if self.rect.right < 0:
            self.kill()
