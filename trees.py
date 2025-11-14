import pygame as pg
from random import choice, randint
import settings
from settings import *
from particles import Particle


class Trees(pg.sprite.Sprite):
    """障碍树木精灵，根据当前移动速度向左滚动。"""

    def __init__(self, tree_type: str, spawn_x: int | None = None) -> None:
        super().__init__()
        file_path = TREE_TYPE.get(tree_type, TREE_TYPE['common_tree'])
        tree_image = pg.image.load(file_path).convert_alpha()
        # 使用设置中的缩放因子使树更矮（并按比例缩放宽度）
        try:
            scale = settings.TREE_SCALE
        except Exception:
            scale = 1.0
        target_w = max(10, int(TREE_WIDTH * scale))
        target_h = max(10, int(TREE_HEIGHT * scale))
        tree_image = pg.transform.scale(tree_image, (target_w, target_h))
        self.image = tree_image
        # 支持外部指定 spawn_x，否则在宽度范围内随机
        if spawn_x is None:
            x = randint(WIDTH, WIDTH * 2)
        else:
            x = spawn_x
        # 把树底部对齐到地面（如果树变矮，仍与地面接触）
        self.rect = self.image.get_rect(midbottom=(x, GROUND_HEIGHT))

    def animation(self) -> None:
        # 支持通过 settings.OBSTACLE_SPEED_MULTIPLIER 调整障碍物速度
        speed = settings.CURRENT_MOVING_SPEED * getattr(settings, 'OBSTACLE_SPEED_MULTIPLIER', 1.0)
        self.rect.x -= speed

    def destroy(self) -> None:
        if self.rect.right < 0:
            self.kill()

    def update(self) -> None:
        self.animation()
        self.destroy()
