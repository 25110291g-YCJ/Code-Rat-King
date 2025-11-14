import pygame as pg
from random import randint
import settings
from settings import *


class Background:
    """管理多层视差背景：天空层与地面层。

    API:
    - update(move_speed): 更新各层 x 偏移
    - draw_sky(surface): 绘制天空层
    - draw_ground_mid(surface): 绘制中景地面（ground_layers[0]）
    - draw_ground_front(surface): 绘制前景地面（ground_layers[1]）
    - reset(): 将所有层的 x 重置为 0
    """

    def __init__(self) -> None:
        # 天空层
        self.sky_layers = []
        try:
            base_sky = pg.image.load(SKY_BACKGROUND).convert()
        except Exception:
            base_sky = pg.Surface((WIDTH, HEIGHT))
            base_sky.fill((135, 206, 235))
        for i, sp in enumerate(getattr(settings, 'PARALLAX_SKY_SPEEDS', [0.45])):
            surf = pg.transform.scale(base_sky, (WIDTH, HEIGHT))
            alpha = max(100, 255 - i * 60)
            try:
                surf.set_alpha(alpha)
            except Exception:
                pass
            self.sky_layers.append({'surf': surf, 'x': 0.0, 'speed': float(sp)})

        # 地面层
        self.ground_layers = []
        try:
            base_ground = pg.image.load(GROUND_BACKGROUND).convert()
        except Exception:
            base_ground = pg.Surface((WIDTH, GROUND_DEPTH))
            base_ground.fill((34, 139, 34))
        for i, sp in enumerate(getattr(settings, 'PARALLAX_GROUND_SPEEDS', [1.0])):
            surf = pg.transform.scale(base_ground, (WIDTH, GROUND_DEPTH))
            alphas = getattr(settings, 'PARALLAX_GROUND_ALPHAS', [255] * len(getattr(settings, 'PARALLAX_GROUND_SPEEDS', [1.0])))
            alpha = alphas[i] if i < len(alphas) else 255
            try:
                surf.set_alpha(alpha)
            except Exception:
                pass
            self.ground_layers.append({'surf': surf, 'x': 0.0, 'speed': float(sp), 'y': GROUND_HEIGHT})

    def update(self, move: float) -> None:
        # 更新偏移量并循环
        for layer in getattr(self, 'sky_layers', []):
            layer['x'] -= move * layer.get('speed', 0.0)
            if layer['x'] <= -WIDTH:
                layer['x'] += WIDTH
        for layer in getattr(self, 'ground_layers', []):
            layer['x'] -= move * layer.get('speed', 0.0)
            if layer['x'] <= -WIDTH:
                layer['x'] += WIDTH

    def draw_sky(self, screen: pg.Surface) -> None:
        for layer in getattr(self, 'sky_layers', []):
            screen.blit(layer['surf'], (int(layer['x']), 0))
            screen.blit(layer['surf'], (int(layer['x']) + WIDTH, 0))

    def draw_ground_mid(self, screen: pg.Surface) -> None:
        if getattr(self, 'ground_layers', None) and len(self.ground_layers) >= 1:
            mid = self.ground_layers[0]
            screen.blit(mid['surf'], (int(mid['x']), mid['y']))
            screen.blit(mid['surf'], (int(mid['x']) + WIDTH, mid['y']))

    def draw_ground_front(self, screen: pg.Surface) -> None:
        if getattr(self, 'ground_layers', None) and len(self.ground_layers) > 1:
            front = self.ground_layers[1]
            screen.blit(front['surf'], (int(front['x']), front['y']))
            screen.blit(front['surf'], (int(front['x']) + WIDTH, front['y']))

    def reset(self) -> None:
        try:
            for l in self.sky_layers:
                l['x'] = 0.0
        except Exception:
            self.sky_layers = []
        try:
            for l in self.ground_layers:
                l['x'] = 0.0
        except Exception:
            self.ground_layers = []
