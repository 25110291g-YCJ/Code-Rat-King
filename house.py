import pygame as pg

import settings
from settings import *


class House(pg.sprite.Sprite):
    """End-house sprite that acts as a level endpoint.

    House 生成在屏幕右侧并随着场景向左移动；当与猫发生重叠时视为到达关卡终点。
    """

    def __init__(self) -> None:
        super().__init__()
        house_image = pg.image.load(HOUSE).convert_alpha()
        self.image = pg.transform.scale(house_image, (HOUSE_WIDTH, HOUSE_HEIGHT))
        self.rect = self.image.get_rect(
            midbottom=(WIDTH + HOUSE_WIDTH, GROUND_HEIGHT + HOUSE_GROUND_OFFSET)
        )

    def animation(self) -> None:
        """Move the house left according to obstacle speed multiplier."""
        # 房屋作为终点也随障碍物速度加速
        speed = settings.CURRENT_MOVING_SPEED * getattr(settings, 'OBSTACLE_SPEED_MULTIPLIER', 1.0)
        self.rect.x -= speed

    def update(self) -> None:
        """Per-frame update: animate and remove when off-screen."""
        self.animation()
        if self.rect.right < 0:
            self.kill()
