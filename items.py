import pygame as pg
import math
import settings
from resources import load_image


class GroundItem(pg.sprite.Sprite):
    """地面道具：支持 'health' 和 'shield' 两种类型。"""

    def __init__(self, item_type: str, spawn_x: int) -> None:
        super().__init__()
        self.type = item_type
        self.orig_life = getattr(settings, 'ITEM_LIFETIME', settings.FPS * 8)
        self.life = self.orig_life
        # 简单绘制：若没有专用贴图，则用基本图形表示
        w, h = 64, 64  # 道具尺寸（缩小一倍：128 -> 64）
        surf = pg.Surface((w, h), pg.SRCALPHA)
        try:
            if self.type == 'health':
                # 血包道具：assets/barrier/0_Archer_Running_007-6.png
                try:
                    img = load_image(getattr(settings, 'HEALTH_ITEM', ''), size=(w, h), convert_alpha=True, crop_transparent=True)
                    surf.blit(img, (0, 0))
                except Exception:
                    surf.fill((220, 40, 60))
            elif self.type == 'shield':
                # 护盾道具：assets/barrier/0_Archer_Running_007-4.png
                try:
                    img = load_image(getattr(settings, 'SHIELD_ITEM', ''), size=(w, h), convert_alpha=True, crop_transparent=True)
                    surf.blit(img, (0, 0))
                except Exception:
                    # 失败时退回到原来的简易护盾图形
                    surf.fill((20, 60, 160))
                    pg.draw.circle(surf, (180, 220, 255), (w // 2, h // 2), 18)
                    pg.draw.circle(surf, (20, 60, 160), (w // 2, h // 2), 12)
            elif self.type == 'superjump':
                # 超级大跳道具：assets/barrier/0_Archer_Running_007-3.png
                try:
                    img = load_image(getattr(settings, 'SUPERJUMP_ITEM', ''), size=(w, h), convert_alpha=True, crop_transparent=True)
                    surf.blit(img, (0, 0))
                except Exception:
                    surf.fill((240, 200, 30))
                    # 画一个简易闪电形状
                    points = [(18, 6), (30, 22), (22, 22), (34, 42), (18, 28), (26, 28)]
                    pg.draw.polygon(surf, (255, 200, 0), points)
            elif self.type == 'coin':
                # 金币道具：assets/barrier/0_Archer_Running_007-5.png
                try:
                    img = load_image(getattr(settings, 'COIN_ITEM', ''), size=(w, h), convert_alpha=True, crop_transparent=True)
                    surf.blit(img, (0, 0))
                except Exception:
                    surf.fill((230, 200, 50))
            else:
                surf.fill((200, 200, 200))
        except Exception:
            surf.fill((200, 200, 200))
            
        # Add glow and floating effect
        glow_margin = 20
        final_w, final_h = w + glow_margin * 2, h + glow_margin * 2
        final_surf = pg.Surface((final_w, final_h), pg.SRCALPHA)
        
        # Glow color based on type
        glow_color = (200, 200, 200, 60)
        if self.type == 'health': glow_color = (255, 50, 50, 100)
        elif self.type == 'shield': glow_color = (50, 100, 255, 100)
        elif self.type == 'superjump': glow_color = (255, 215, 0, 100)
        elif self.type == 'coin': glow_color = (255, 255, 50, 100)
        
        # Draw glow
        center = (final_w // 2, final_h // 2)
        pg.draw.circle(final_surf, glow_color, center, w // 2 + 15)
        pg.draw.circle(final_surf, (*glow_color[:3], 40), center, w // 2 + 25)
        
        # Blit item
        final_surf.blit(surf, (glow_margin, glow_margin))
        
        self.image = final_surf
        # Spawn slightly higher than ground to hover
        self.rect = self.image.get_rect(midbottom=(spawn_x, settings.GROUND_HEIGHT - 30))
        
        self.base_y = self.rect.centery
        self.float_timer = 0

    def update(self) -> None:
        # Move left
        speed = settings.CURRENT_MOVING_SPEED * getattr(settings, 'OBSTACLE_SPEED_MULTIPLIER', 1.0)
        self.rect.x -= speed
        
        # Float up and down
        self.float_timer += 0.1
        self.rect.centery = self.base_y + math.sin(self.float_timer) * 10
        
        self.life -= 1
        if self.rect.right < 0 or self.life <= 0:
            self.kill()
