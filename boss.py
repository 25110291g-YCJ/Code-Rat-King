"""Boss 敌人和子弹系统"""
import pygame as pg
from settings import *
import settings
from random import choice, randint
import os
from resources import list_pngs, load_image


class Bullet(pg.sprite.Sprite):
    """Boss 发射的子弹"""
    
    def __init__(self, x: int, y: int, bullet_type: str):
        """
        初始化子弹
        
        Args:
            x: 子弹初始X坐标
            y: 子弹初始Y坐标
            bullet_type: 子弹类型 ('A', 'B', 'C')
                A - 低位子弹（玩家需要滑行躲避）
                B - 中位子弹（玩家站立不动即可躲避）
                C - 高位子弹（玩家需要跳跃躲避）
        """
        super().__init__()
        self.bullet_type = bullet_type
        
        # 子弹尺寸和颜色（根据类型）
        bullet_size = getattr(settings, 'BULLET_SIZE', 20)
        
        # 不同类型子弹使用不同颜色
        if bullet_type == 'A':
            # color = (255, 100, 100)  # 红色 - 低位
            self.height_range = 'low'
        elif bullet_type == 'B':
            # color = (100, 255, 100)  # 绿色 - 中位
            self.height_range = 'mid'
        else:  # C
            # color = (100, 100, 255)  # 蓝色 - 高位
            self.height_range = 'high'
        
        # 创建子弹图像
        # 使用 barrier.png 替换原有的色块
        self.image = load_image('assets/barrier/barrier.png', size=(bullet_size, bullet_size))
        
        self.rect = self.image.get_rect(center=(x, y))
        
        # 子弹速度（向左移动）
        self.speed = getattr(settings, 'BULLET_SPEED', 8)
    
    def update(self) -> None:
        """更新子弹位置"""
        self.rect.x -= self.speed
        
        # 如果子弹移出屏幕左侧，删除
        if self.rect.right < 0:
            self.kill()


class Boss(pg.sprite.Sprite):
    """Boss 敌人"""
    
    def __init__(self, boss_name: str = 'simon'):
        super().__init__()
        
        # Boss 尺寸
        self.boss_width = getattr(settings, 'BOSS_WIDTH', 200)
        self.boss_height = getattr(settings, 'BOSS_HEIGHT', 200)
        
        # 加载 Boss 动画帧
        self.frames = []
        self.frame_index = 0
        self.animation_speed = 0.15
        
        try:
            # 尝试加载指定 Boss 的动画帧
            # 映射 boss_name 到文件夹名 (simon, david, gio)
            # 确保 boss_name 是小写
            name = boss_name.lower()
            folder_path = os.path.join('assets', 'boss', 'boss', name)
            
            # 如果文件夹不存在，尝试直接用 boss_name (兼容旧逻辑)
            if not os.path.exists(folder_path):
                 # 尝试默认路径
                 pass

            frame_files = list_pngs(folder_path)
            
            if not frame_files:
                # 如果找不到，尝试加载默认 Idle
                # print(f"Warning: No frames found for boss '{name}', using default.")
                try:
                    boss_img = pg.image.load('assets/boss/Idle_000.png').convert_alpha()
                    self.frames = [pg.transform.scale(boss_img, (self.boss_width, self.boss_height))]
                except:
                    raise Exception("Default image not found")
            else:
                for f in frame_files:
                    img = load_image(f, size=(self.boss_width, self.boss_height), convert_alpha=True)
                    self.frames.append(img)
                    
        except Exception as e:
            print(f"Warning: Failed to load boss image: {e}")
            # 使用占位图像
            self.image = pg.Surface((self.boss_width, self.boss_height))
            self.image.fill((128, 0, 128))  # 紫色占位
            pg.draw.rect(self.image, (255, 255, 255), self.image.get_rect(), 3)
            self.frames = [self.image]
            
        self.image = self.frames[0]
        
        # Boss 位置（屏幕右侧）
        boss_x = getattr(settings, 'BOSS_X_POSITION', WIDTH - 150)
        boss_y = HEIGHT // 2
        self.rect = self.image.get_rect(center=(boss_x, boss_y))
        
        # 垂直移动相关
        self.move_direction = 1  # 1向下，-1向上
        self.move_speed = getattr(settings, 'BOSS_MOVE_SPEED', 2)
        self.move_range_top = getattr(settings, 'BOSS_MOVE_TOP', 150)
        self.move_range_bottom = getattr(settings, 'BOSS_MOVE_BOTTOM', HEIGHT - 250)
        
        # 射击相关
        self.shoot_timer = 0
        
        # 根据 Boss 名字获取射击间隔
        intervals = getattr(settings, 'BOSS_SHOOT_INTERVALS', {})
        default_interval = getattr(settings, 'BOSS_SHOOT_INTERVAL_DEFAULT', 180)
        self.shoot_interval = intervals.get(boss_name.lower(), default_interval)
        
        # 三个发射位置（A, B, C）的Y坐标
        # A: 中位（玩家需要滑行躲避）- 在玩家高度中间，滑行可躲避
        self.position_A_y = GROUND_HEIGHT + getattr(settings, 'PLAYER_GROUND_OFFSET', 33) - (getattr(settings, 'PLAYER_HEIGHT', 200) // 2)
        # B: 高位（玩家站立不动可躲避）- 在玩家头部上方，跳跃会被击中
        self.position_B_y = GROUND_HEIGHT + getattr(settings, 'PLAYER_GROUND_OFFSET', 33) - getattr(settings, 'PLAYER_HEIGHT', 200) - 20
        # C: 低位（玩家需要跳跃躲避）- 在玩家正前方，站立会被击中
        self.position_C_y = GROUND_HEIGHT + getattr(settings, 'PLAYER_GROUND_OFFSET', 33) - 60
        
        # 子弹发射X位置（Boss左侧）
        self.bullet_spawn_x = self.rect.left - 10
    
    def update(self) -> None:
        """更新 Boss 状态"""
        # 动画更新
        self.frame_index += self.animation_speed
        if self.frame_index >= len(self.frames):
            self.frame_index = 0
        self.image = self.frames[int(self.frame_index)]

        # 上下移动
        self.rect.y += self.move_speed * self.move_direction
        
        # 边界检测，改变方向
        if self.rect.top <= self.move_range_top:
            self.move_direction = 1  # 向下
            self.rect.top = self.move_range_top
        elif self.rect.bottom >= self.move_range_bottom:
            self.move_direction = -1  # 向上
            self.rect.bottom = self.move_range_bottom
        
        # 更新射击计时器
        self.shoot_timer += 1
    
    def should_shoot(self) -> bool:
        """检查是否应该发射子弹"""
        if self.shoot_timer >= self.shoot_interval:
            self.shoot_timer = 0
            return True
        return False
    
    def get_bullet_position(self) -> tuple:
        """
        随机选择一个发射位置并返回坐标和类型
        
        Returns:
            (x, y, type): 子弹坐标和类型
        """
        # 随机选择发射位置
        bullet_type = choice(['A', 'B', 'C'])
        
        if bullet_type == 'A':
            y = self.position_A_y
        elif bullet_type == 'B':
            y = self.position_B_y
        else:  # C
            y = self.position_C_y
        
        return (self.bullet_spawn_x, y, bullet_type)
