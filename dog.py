import pygame as pg
from random import randint

import settings
from settings import *


class Dog(pg.sprite.Sprite):
    """彩蛋狗狗精灵，偶尔乱入并随着玩家得分而提速。

    这个类与之前放在主文件中的实现保持一致，被拆分到独立模块以便复用。
    """

    def __init__(self) -> None:
        super().__init__()
        self.dog_index = 0
        self.dog_run = []
        for frame in DOG_RUN:
            dog_image = pg.image.load(frame).convert_alpha()
            dog_image = pg.transform.scale(dog_image, (DOG_WIDTH, DOG_HEIGHT))
            self.dog_run.append(dog_image)
        self.image = self.dog_run[self.dog_index]
        self.rect = self.image.get_rect(midbottom=(WIDTH + DOG_WIDTH, GROUND_HEIGHT))

    def run(self) -> None:
        """每帧移动狗狗：按场景速度向左移动并在移出屏幕后销毁。"""
        # 狗狗速度应与障碍物速度基于同一倍率放大
        speed = settings.CURRENT_MOVING_SPEED * getattr(settings, 'OBSTACLE_SPEED_MULTIPLIER', 1.0) * 2
        self.rect.x -= speed
        if self.rect.right < 0:
            self.kill()

    def animation(self) -> None:
        """Advance animation frame index and update displayed image."""
        self.dog_index += 0.2
        if self.dog_index >= len(self.dog_run):
            self.dog_index = 0
        self.image = self.dog_run[int(self.dog_index)]

    def update(self) -> None:
        """Standard pygame Sprite update: move and animate."""
        self.run()
        self.animation()
