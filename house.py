import pygame as pg
import os
import settings
from settings import *


class House(pg.sprite.Sprite):
    """终点房屋，猫碰到后视为通关。"""

    def __init__(self, level_index: int = 0) -> None:
        super().__init__()
        
        # 根据关卡索引选择对应的出口图片
        # 0: scene1 -> 场景1出口.PNG
        # 1: scene2 -> 场景2出口.PNG
        # 2: scene3 -> 场景3出口.PNG
        base_path = os.path.join('assets', 'background', 'coding')
        if level_index == 0:
            img_path = os.path.join(base_path, '场景1出口.PNG')
        elif level_index == 1:
            img_path = os.path.join(base_path, '场景2出口.PNG')
        elif level_index == 2:
            img_path = os.path.join(base_path, '场景3出口.PNG')
        else:
            img_path = HOUSE  # fallback

        try:
            house_image = pg.image.load(img_path).convert_alpha()
        except Exception:
            # 如果加载失败，回退到默认房子
            try:
                house_image = pg.image.load(HOUSE).convert_alpha()
            except:
                house_image = pg.Surface((HOUSE_WIDTH, HOUSE_HEIGHT))
                house_image.fill((200, 100, 100))

        # 保持原有尺寸缩放逻辑，或者根据新图片调整
        # 获取原始尺寸
        orig_w, orig_h = house_image.get_size()
        
        # 设定目标高度（调大一些，比如 550 像素，约为地面上方空间的 80%）
        target_h = 550
        
        # 按比例计算宽度，保持图片正常比例
        if orig_h > 0:
            scale_ratio = target_h / orig_h
            target_w = int(orig_w * scale_ratio)
        else:
            target_w, target_h = HOUSE_WIDTH, HOUSE_HEIGHT

        self.image = pg.transform.scale(house_image, (target_w, target_h))
        self.rect = self.image.get_rect(
            midbottom=(WIDTH + target_w, GROUND_HEIGHT + HOUSE_GROUND_OFFSET)
        )

    def animation(self) -> None:
        # 房屋作为终点也随障碍物速度加速
        speed = settings.CURRENT_MOVING_SPEED * getattr(settings, 'OBSTACLE_SPEED_MULTIPLIER', 1.0)
        self.rect.x -= speed

    def update(self) -> None:
        self.animation()
        if self.rect.right < 0:
            self.kill()
