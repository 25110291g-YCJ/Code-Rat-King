import pygame as pg
import settings
from settings import *
from resources import load_image


class GroundItem(pg.sprite.Sprite):
    """GroundItem 表示地图上的可拾取道具。

    支持类型包括：'health'（回血）、'shield'（临时护盾）、'superjump'（一次超级跳）和 'coin'（加分）。
    - __init__(item_type, spawn_x): 根据类型尝试加载贴图并设置初始生命（用于过期自动销毁）。
    - update(): 每帧随场景向左移动并衰减 life，超出屏幕或生命为 0 时自杀（kill）。
    """

    def __init__(self, item_type: str, spawn_x: int) -> None:
        """Create an item of given type at horizontal position spawn_x.

        spawn_x: 世界坐标（通常 >= WIDTH），用于在屏幕右侧生成道具。
        """
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
            elif self.type == 'coin':
                # 尝试加载金币图片
                try:
                    img = load_image(getattr(settings, 'COIN_ITEM', ''), size=(w, h), convert_alpha=True)
                    surf.blit(img, (0, 0))
                except Exception:
                    # fallback: yellow circle
                    surf.fill((0, 0, 0, 0))
                    pg.draw.circle(surf, (240, 200, 0), (w // 2, h // 2), 18)
                    pg.draw.circle(surf, (200, 140, 0), (w // 2, h // 2), 12)
            else:
                surf.fill((200, 200, 200))
        except Exception:
            surf.fill((200, 200, 200))
        self.image = surf
        self.rect = self.image.get_rect(midbottom=(spawn_x, GROUND_HEIGHT))

    def update(self) -> None:
        """Per-frame update: move left with scene speed and decrease life.

        当道具移出左侧屏幕或其 life 用尽时会被移除。
        """
        # 随场景左移
        speed = settings.CURRENT_MOVING_SPEED * getattr(settings, 'OBSTACLE_SPEED_MULTIPLIER', 1.0)
        self.rect.x -= speed
        self.life -= 1
        if self.rect.right < 0 or self.life <= 0:
            self.kill()
