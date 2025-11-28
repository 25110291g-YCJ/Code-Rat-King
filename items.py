import pygame as pg
import settings
from settings import *
from resources import load_image


class GroundItem(pg.sprite.Sprite):
    """地面道具：支持 'health' 和 'shield' 两种类型。"""

    def __init__(self, item_type: str, spawn_x: int) -> None:
        super().__init__()
        self.type = item_type
        self.orig_life = getattr(settings, 'ITEM_LIFETIME', FPS * 8)
        self.life = self.orig_life
        # 简单绘制：若没有专用贴图，则用基本图形表示
        w, h = 48, 48
        surf = pg.Surface((w, h), pg.SRCALPHA)
        try:
            if self.type == 'health':
                # 使用指定的图片资源（HEALTH_ITEM），若加载失败则退回为纯红色方块
                try:
                    img = load_image(getattr(settings, 'HEALTH_ITEM', ''), size=(w, h), convert_alpha=True)
                    surf.blit(img, (0, 0))
                except Exception:
                    surf.fill((220, 40, 60))
            elif self.type == 'shield':
                surf.fill((20, 60, 160))
                pg.draw.circle(surf, (180, 220, 255), (w // 2, h // 2), 18)
                pg.draw.circle(surf, (20, 60, 160), (w // 2, h // 2), 12)
            elif self.type == 'superjump':
                # 尝试加载外部贴图（用户提供的闪电图片），若失败使用简单图形替代
                try:
                    img = load_image(getattr(settings, 'SUPERJUMP_ITEM', ''), size=(w, h), convert_alpha=True)
                    surf.blit(img, (0, 0))
                except Exception:
                    surf.fill((240, 200, 30))
                    # 画一个简易闪电形状
                    points = [(18, 6), (30, 22), (22, 22), (34, 42), (18, 28), (26, 28)]
                    pg.draw.polygon(surf, (255, 200, 0), points)
            else:
                surf.fill((200, 200, 200))
        except Exception:
            surf.fill((200, 200, 200))
        self.image = surf
        self.rect = self.image.get_rect(midbottom=(spawn_x, GROUND_HEIGHT))

    def update(self) -> None:
        # 随场景左移
        speed = settings.CURRENT_MOVING_SPEED * getattr(settings, 'OBSTACLE_SPEED_MULTIPLIER', 1.0)
        self.rect.x -= speed
        self.life -= 1
        if self.rect.right < 0 or self.life <= 0:
            self.kill()
