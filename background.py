import pygame as pg
from random import randint
import settings
from settings import *
import os
import glob
from resources import load_image, list_pngs


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
        # 按关卡名加载背景的通用字段
        self.current_level = 'sky'
        self.sky_layers = []
        self.ground_layers = []

        # 初始化为 sky（默认行为）；具体加载委托给 set_level
        try:
            self.set_level('sky')
        except Exception:
            # 回退：按旧逻辑构建简单的 sky + ground 占位层
            try:
                base_sky = load_image(SKY_BACKGROUND, size=(WIDTH, HEIGHT), convert_alpha=False)
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

            try:
                base_ground = load_image(GROUND_BACKGROUND, size=(WIDTH, GROUND_DEPTH), convert_alpha=False)
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

        # 兼容字段（在 set_level 中会赋值）：用于自定义目录（如 Mine/Volcano）加载后作为层使用
        self.custom_layers = []
        self.custom_ground = None
        self.custom_timer = 0

    def update(self, move: float) -> None:
        # 更新偏移量并循环
        # 若为自定义关卡（Mine/Volcano 等），优先更新 custom_layers
        if getattr(self, 'current_level', 'sky') != 'sky' and getattr(self, 'custom_layers', None):
            for layer in self.custom_layers:
                layer['x'] -= move * layer.get('speed', 0.0)
                if layer['x'] <= -WIDTH:
                    layer['x'] += WIDTH
            # 如果 custom_timer 在倒计时，消耗它（兼容旧的临时背景行为）
            try:
                if getattr(self, 'custom_timer', 0) > 0:
                    self.custom_timer -= 1
                else:
                    # 不自动回退：关卡切换由外部控制
                    pass
            except Exception:
                pass
        else:
            for layer in getattr(self, 'sky_layers', []):
                layer['x'] -= move * layer.get('speed', 0.0)
                if layer['x'] <= -WIDTH:
                    layer['x'] += WIDTH
        for layer in getattr(self, 'ground_layers', []):
            layer['x'] -= move * layer.get('speed', 0.0)
            if layer['x'] <= -WIDTH:
                layer['x'] += WIDTH
        # 若 custom_ground 存在，也需更新其 x
        if getattr(self, 'custom_ground', None):
            try:
                self.custom_ground['x'] -= move * self.custom_ground.get('speed', 0.0)
                if self.custom_ground['x'] <= -WIDTH:
                    self.custom_ground['x'] += WIDTH
            except Exception:
                pass

    def draw_sky(self, screen: pg.Surface) -> None:
        # 如果为自定义关卡（custom_layers），优先绘制 custom_layers
        if getattr(self, 'current_level', 'sky') != 'sky' and getattr(self, 'custom_layers', None):
            for layer in self.custom_layers:
                screen.blit(layer['surf'], (int(layer['x']), 0))
                screen.blit(layer['surf'], (int(layer['x']) + WIDTH, 0))
            return
        for layer in getattr(self, 'sky_layers', []):
            screen.blit(layer['surf'], (int(layer['x']), 0))
            screen.blit(layer['surf'], (int(layer['x']) + WIDTH, 0))

    def draw_ground_mid(self, screen: pg.Surface) -> None:
        # 如果 custom_ground 存在，绘制它作为地面
        if getattr(self, 'custom_ground', None):
            try:
                screen.blit(self.custom_ground['surf'], (int(self.custom_ground['x']), self.custom_ground['y']))
                screen.blit(self.custom_ground['surf'], (int(self.custom_ground['x']) + WIDTH, self.custom_ground['y']))
                return
            except Exception:
                pass
        if getattr(self, 'ground_layers', None) and len(self.ground_layers) >= 1:
            mid = self.ground_layers[0]
            screen.blit(mid['surf'], (int(mid['x']), mid['y']))
            screen.blit(mid['surf'], (int(mid['x']) + WIDTH, mid['y']))

    def draw_ground_front(self, screen: pg.Surface) -> None:
        # Scene 1, 2 和 3 已经调整了背景高度，不需要前景覆盖，否则会遮挡
        if getattr(self, 'current_level', '') in ['scene1', 'scene2', 'scene3']:
            return

        # custom 层作为前景（若存在多层）
        if getattr(self, 'current_level', 'sky') != 'sky' and getattr(self, 'custom_layers', None):
            try:
                if len(self.custom_layers) > 1:
                    front = self.custom_layers[-2]
                    screen.blit(front['surf'], (int(front['x']), GROUND_HEIGHT))
                    screen.blit(front['surf'], (int(front['x']) + WIDTH, GROUND_HEIGHT))
                    return
            except Exception:
                pass
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

    def set_level(self, level_name: str) -> None:
        """切换到指定关卡背景。

        level_name: 'sky' (默认)，'mine'，'voclano'（映射到 assets/background/Volcano）
        """
        name = (level_name or 'sky').lower()
        self.current_level = name
        # 清理旧的 custom 数据
        self.custom_layers = []
        self.custom_ground = None
        self.custom_timer = 0

        if name == 'sky':
            # 还原为默认 SKY + GROUND
            try:
                base_sky = load_image(SKY_BACKGROUND, size=(WIDTH, HEIGHT), convert_alpha=False)
            except Exception:
                base_sky = pg.Surface((WIDTH, HEIGHT))
                base_sky.fill((135, 206, 235))
            self.sky_layers = []
            for i, sp in enumerate(getattr(settings, 'PARALLAX_SKY_SPEEDS', [0.45])):
                surf = pg.transform.scale(base_sky, (WIDTH, HEIGHT))
                alpha = max(100, 255 - i * 60)
                try:
                    surf.set_alpha(alpha)
                except Exception:
                    pass
                self.sky_layers.append({'surf': surf, 'x': 0.0, 'speed': float(sp)})

            try:
                base_ground = load_image(GROUND_BACKGROUND, size=(WIDTH, GROUND_DEPTH), convert_alpha=False)
            except Exception:
                base_ground = pg.Surface((WIDTH, GROUND_DEPTH))
                base_ground.fill((34, 139, 34))
            self.ground_layers = []
            for i, sp in enumerate(getattr(settings, 'PARALLAX_GROUND_SPEEDS', [1.0])):
                surf = pg.transform.scale(base_ground, (WIDTH, GROUND_DEPTH))
                alphas = getattr(settings, 'PARALLAX_GROUND_ALPHAS', [255] * len(getattr(settings, 'PARALLAX_GROUND_SPEEDS', [1.0])))
                alpha = alphas[i] if i < len(alphas) else 255
                try:
                    surf.set_alpha(alpha)
                except Exception:
                    pass
                self.ground_layers.append({'surf': surf, 'x': 0.0, 'speed': float(sp), 'y': GROUND_HEIGHT})
            return

        # 处理新的 coding 场景
        if name in ['scene1', 'scene2', 'scene3']:
            base_path = os.path.join('assets', 'background', 'coding')
            
            # 默认尺寸
            target_width = WIDTH
            target_height = HEIGHT

            if name == 'scene1':
                # Scene 1: 背景 + 固定装饰
                try:
                    # 1. 加载基础背景
                    bg_path = os.path.join(base_path, '场景1背景.PNG')
                    bg_surf = load_image(bg_path, size=(target_width, target_height), convert_alpha=True)
                    
                    # 2. 加载并合成装饰 (IMG_5503, 5504, 5505)
                    # 统一放置在背景上方，并保持相同高度
                    fixed_y = 50
                    fixed_h = 500  # 调大高度 (250 -> 500)
                    
                    decos = [
                        (os.path.join('assets', 'documation', 'IMG_5503.PNG'), int(target_width * 0.2)),
                        (os.path.join('assets', 'documation', 'IMG_5504.PNG'), int(target_width * 0.5)),
                        (os.path.join('assets', 'documation', 'IMG_5505.PNG'), int(target_width * 0.8)),
                        # 新增装饰
                        (os.path.join('assets', 'documation', 'IMG_5505.PNG'), int(target_width * 0.1)),
                        (os.path.join('assets', 'documation', 'IMG_5504.PNG'), int(target_width * 0.3))
                    ]
                    
                    for path, x_pos in decos:
                        try:
                            dec_img = load_image(path, convert_alpha=True)
                            
                            # 针对 IMG_5503 特殊处理高度（小一点）
                            current_h = fixed_h
                            align_bottom = False
                            
                            if 'IMG_5503' in path:
                                current_h = 250  # 其他是 500，这个设为一半
                            
                            # 针对 IMG_5505 (终点门) 特殊处理：贴住地面
                            if 'IMG_5505' in path:
                                align_bottom = True
                            
                            # 统一缩放到固定高度
                            scale = current_h / dec_img.get_height()
                            dec_img = pg.transform.scale(dec_img, (int(dec_img.get_width() * scale), current_h))
                            
                            rect = dec_img.get_rect()
                            rect.x = x_pos
                            
                            if align_bottom:
                                rect.bottom = target_height
                            else:
                                rect.y = fixed_y
                                
                            bg_surf.blit(dec_img, rect)
                        except Exception:
                            pass
                            
                    self.custom_layers = [{'surf': bg_surf, 'x': 0.0, 'speed': 0.2}]
                except Exception:
                    pass

            elif name == 'scene2':
                # Scene 2: 背景 + 固定装饰 (IMG_5501, IMG_5502)
                try:
                    # 1. 加载基础背景
                    bg_path = os.path.join(base_path, '场景2背景.PNG')
                    bg_surf = load_image(bg_path, size=(target_width, target_height), convert_alpha=True)
                    
                    # 2. 加载并合成装饰 (IMG_5501, IMG_5502)
                    # 统一放置在背景上方，并保持相同高度
                    fixed_y = 50
                    fixed_h = 500
                    
                    decos = [
                        (os.path.join('assets', 'documation', 'IMG_5501.PNG'), int(target_width * 0.2)),
                        (os.path.join('assets', 'documation', 'IMG_5502.PNG'), int(target_width * 0.6))
                    ]
                    
                    for path, x_pos in decos:
                        try:
                            dec_img = load_image(path, convert_alpha=True)
                            
                            current_h = fixed_h
                            align_bottom = False
                            
                            # 针对 IMG_5502 特殊处理：调大一点，并贴住地面
                            if 'IMG_5502' in path:
                                current_h = 650
                                align_bottom = True
                            
                            # 统一缩放到固定高度
                            scale = current_h / dec_img.get_height()
                            dec_img = pg.transform.scale(dec_img, (int(dec_img.get_width() * scale), current_h))
                            
                            rect = dec_img.get_rect()
                            rect.x = x_pos
                            
                            if align_bottom:
                                rect.bottom = target_height
                            else:
                                rect.y = fixed_y
                                
                            bg_surf.blit(dec_img, rect)
                        except Exception:
                            pass
                            
                    self.custom_layers = [{'surf': bg_surf, 'x': 0.0, 'speed': 0.2}]
                except Exception:
                    pass

            elif name == 'scene3':
                # Scene 3: 背景 + 窗户/垃圾桶 + 固定装饰
                try:
                    # 1. 加载基础背景
                    bg_path = os.path.join(base_path, '场景3背景.PNG')
                    bg_surf = load_image(bg_path, size=(target_width, target_height), convert_alpha=True)
                    
                    # 2. 叠加原有的窗户和垃圾桶 (假设它们是全屏图层)
                    overlays = ['场景3窗户.PNG', '场景3垃圾桶.PNG']
                    for ov in overlays:
                        try:
                            ov_img = load_image(os.path.join(base_path, ov), size=(target_width, target_height), convert_alpha=True)
                            bg_surf.blit(ov_img, (0, 0))
                        except Exception:
                            pass
                            
                    self.custom_layers = [{'surf': bg_surf, 'x': 0.0, 'speed': 0.2}]
                except Exception:
                    pass
            else:
                files = []
            
            # files = [os.path.join(base_path, f) for f in filenames] # 已在上方构建完整路径
            
            # Load layers (仅对非 Scene 1/3 的情况，或者 Scene 2 使用)
            if name not in ['scene1', 'scene3']:
                # ...existing logic for scene 2 or others...
                pass
            
            # Set custom ground (使用最后一层作为地面参考)
            
            # Set custom ground (使用最后一层作为地面参考)
            try:
                if name in ['scene1', 'scene2', 'scene3']:
                    # Scene 1, 2 和 3 使用纯灰色地面
                    g_surf = pg.Surface((WIDTH, GROUND_DEPTH))
                    g_surf.fill((100, 100, 100))
                    self.custom_ground = {'surf': g_surf, 'x': 0.0, 'speed': 1.0, 'y': GROUND_HEIGHT}
                elif self.custom_layers:
                    last = self.custom_layers[-1]
                    ground_surf = pg.transform.scale(last['surf'], (WIDTH, GROUND_DEPTH))
                    self.custom_ground = {'surf': ground_surf, 'x': 0.0, 'speed': float(last.get('speed', 1.0)), 'y': GROUND_HEIGHT}
            except Exception:
                self.custom_ground = None
            return

        # 试图加载自定义文件夹下的 png 作为分层图（支持 Mine, Volcano 等）
        folder_map = {'mine': 'Mine', 'voclano': 'Volcano', 'volcano': 'Volcano'}
        folder = folder_map.get(name, name)
        try:
            files = list_pngs(os.path.join('assets', 'background', folder))
        except Exception:
            files = []
        if not files:
            # 回退到 sky
            return self.set_level('sky')

        # 将每张图作为一层（从远到近排列），并生成速度因子
        base_speed = 0.12
        speed_step = 0.12
        self.custom_layers = []
        for i, fp in enumerate(files):
            try:
                img = load_image(fp, size=(WIDTH, HEIGHT), convert_alpha=True)
                speed = base_speed + i * speed_step
                self.custom_layers.append({'surf': img, 'x': 0.0, 'speed': float(speed)})
            except Exception:
                continue

        # custom_ground 使用最后一层的缩放为 ground_depth（尝试兼容）
        try:
            last = self.custom_layers[-1]
            ground_surf = pg.transform.scale(last['surf'], (WIDTH, GROUND_DEPTH))
            self.custom_ground = {'surf': ground_surf, 'x': 0.0, 'speed': float(self.custom_layers[-1].get('speed', 1.0)), 'y': GROUND_HEIGHT}
        except Exception:
            self.custom_ground = None
