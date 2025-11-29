import pygame as pg
from settings import *
import settings
import os
import glob


class Player(pg.sprite.Sprite):
    """游戏中玩家角色精灵的类，负责处理跳跃、滑行、动画与惩罚状态。"""

    def __init__(self) -> None:
        super().__init__()
        self.gravity = 0
        self.anim_index = 0
        self.penalty_timer = 0
        # 碰撞无敌计时器，避免多帧重复扣血
        self.damage_timer = 0
        self.super_jump_ready = False
        self.super_jump_effect_timer = 0
        # 新规则：每成功触发三次跳跃后，下一次跳跃为超级跳跃
        self.jumps_since_charge = 0
        self.next_jump_super = False
        # 用于追踪上一帧是否在空中，便于检测着陆事件
        self.was_in_air = False
        
        # 滑行状态
        self.is_sliding = False
        self.slide_timer = 0
        self.slide_cooldown = 0  # 滑行冷却时间
        
        # 角色尺寸（可根据实际资源调整）
        self.char_width = getattr(settings, 'PLAYER_WIDTH', settings.CAT_WIDTH)
        self.char_height = getattr(settings, 'PLAYER_HEIGHT', settings.CAT_HEIGHT)
        
        # 加载各种动画
        self._load_animations()
        
        # 获取地面偏移量（修正角色脚部位置）
        self.ground_offset = getattr(settings, 'PLAYER_GROUND_OFFSET', 0)
        
        # 初始图像和位置
        self.image = self.idle_frames[0] if self.idle_frames else pg.Surface((self.char_width, self.char_height))
        self.rect = self.image.get_rect(midbottom=(settings.CAT_START_X, settings.GROUND_HEIGHT + self.ground_offset))
        
        # 站立姿势（用于开始界面）- 使用cat_stand保持兼容性
        self.cat_stand = pg.transform.scale(self.image, (self.char_width * 2, self.char_height * 2))
        self.cat_stand_rect = self.cat_stand.get_rect(center=(settings.CAT_START_X, settings.HEIGHT // 2))
        
        # 音效
        self.jump_sound = pg.mixer.Sound(settings.JUMP_SOUND)
        try:
            self.slide_sound = pg.mixer.Sound('assets/sound effect/slide.wav')
        except:
            self.slide_sound = None

    def _load_animations(self) -> None:
        """加载角色的各种动画帧。"""
        # 修改为新的资源路径 assets/shushu
        base_path = 'assets/shushu'
        
        # 加载跑步动画
        self.run_frames = self._load_animation_frames(os.path.join(base_path, 'run'), self.char_width, self.char_height)
        
        # 加载待机动画 (使用跑步的第一帧作为待机)
        if self.run_frames:
            self.idle_frames = [self.run_frames[0]]
        else:
            self.idle_frames = []
        
        # 加载跳跃动画
        self.jump_frames = self._load_animation_frames(os.path.join(base_path, 'jump'), self.char_width, self.char_height)
        
        # 加载滑行动画 (对应 dun 文件夹)
        self.slide_frames = self._load_animation_frames(os.path.join(base_path, 'dun'), self.char_width, self.char_height)
        
        # 加载受伤动画 (暂无，使用跑步帧代替)
        self.hurt_frames = self.run_frames
        
        # 如果某个动画加载失败，使用备用
        if not self.idle_frames:
            self.idle_frames = [pg.Surface((self.char_width, self.char_height))]
        if not self.run_frames:
            self.run_frames = self.idle_frames
        if not self.jump_frames:
            self.jump_frames = self.run_frames
        if not self.slide_frames:
            self.slide_frames = self.run_frames

    def _load_animation_frames(self, folder_path: str, width: int, height: int) -> list:
        """从指定文件夹加载动画帧。"""
        frames = []
        try:
            # 获取文件夹中的所有PNG文件并排序
            pattern = os.path.join(folder_path, '*.png')
            files = sorted(glob.glob(pattern))
            
            for file_path in files:
                try:
                    img = pg.image.load(file_path).convert_alpha()
                    img = pg.transform.scale(img, (width, height))
                    frames.append(img)
                except Exception as e:
                    print(f"Warning: Failed to load {file_path}: {e}")
                    continue
        except Exception as e:
            print(f"Warning: Failed to load animation from {folder_path}: {e}")
        
        return frames

    def start_jump(self) -> None:
        """在收到正确打字事件时尝试起跳。"""
        # 滑行状态下不能跳跃
        if self.is_sliding:
            return
            
        if self.rect.bottom >= GROUND_HEIGHT + self.ground_offset and self.penalty_timer <= 0:
            self.anim_index = 0
            # 如果已标记下一次为超级跳或通过其他方式激活了超级跳，执行超级跳并重置计数
            if getattr(self, 'next_jump_super', False) or getattr(self, 'super_jump_ready', False):
                jump_force = SUPER_JUMP_FORCE
                # 消耗超级跳并重置计数
                self.next_jump_super = False
                self.super_jump_ready = False
                self.jumps_since_charge = 0
                self.super_jump_effect_timer = SUPER_JUMP_EFFECT_FRAMES
            else:
                # 普通跳跃，累加跳跃计数；当累计3次后标记下一次为超级跳（但当前仍为普通跳）
                jump_force = GRAVITY
                try:
                    self.jumps_since_charge += 1
                except Exception:
                    self.jumps_since_charge = 1
                if self.jumps_since_charge >= 3:
                    self.next_jump_super = True
                    # 同步显示状态（使用 super_jump_ready 来驱动 HUD 显示）
                    self.super_jump_ready = True
                    self.super_jump_effect_timer = SUPER_JUMP_EFFECT_FRAMES
            self.gravity = jump_force
            self.rect.y += self.gravity
            self.jump_sound.play()

    def start_slide(self) -> None:
        """开始滑行。"""
        # 只有在地面上且不在冷却期才能滑行
        if self.rect.bottom >= GROUND_HEIGHT + self.ground_offset and self.slide_cooldown <= 0 and not self.is_sliding:
            self.is_sliding = True
            self.slide_timer = getattr(settings, 'SLIDE_DURATION', 30)  # 滑行持续时间（帧）
            self.slide_cooldown = getattr(settings, 'SLIDE_COOLDOWN', 60)  # 滑行冷却时间（帧）
            self.anim_index = 0
            
            # 滑行时降低碰撞箱高度，但保持底部在地面上
            self.rect.height = int(self.char_height * 0.5)  # 碰撞箱高度减半
            self.rect.bottom = GROUND_HEIGHT + self.ground_offset  # 确保底部始终在地面
            
            # 播放滑行音效
            if self.slide_sound:
                try:
                    self.slide_sound.play()
                except:
                    pass

    def apply_penalty(self) -> None:
        """触发惩罚状态，短时间内禁止再次跳跃。"""
        self.penalty_timer = PENALTY_LOCK_FRAMES
        if self.rect.bottom <= GROUND_HEIGHT + self.ground_offset:
            self.gravity = abs(self.gravity)

    def enable_super_jump(self) -> None:
        """激活超级跳跃奖励。"""
        # 通过事件触发的超级跳也作为下一次可用的超级跳（与基于跳跃计数的规则一致）
        self.super_jump_ready = True
        self.next_jump_super = True
        self.super_jump_effect_timer = SUPER_JUMP_EFFECT_FRAMES

    def handle_gravity(self) -> None:
        """根据重力效果更新角色的垂直位置。"""
        prev_bottom = self.rect.bottom
        if self.rect.bottom < GROUND_HEIGHT + self.ground_offset:
            self.gravity += 1
        else:
            self.rect.bottom = GROUND_HEIGHT + self.ground_offset
            self.gravity = 0
        self.rect.y += self.gravity

        # 如果上一帧在空中而本帧着地，则触发着陆事件以生成尘土粒子
        if prev_bottom < GROUND_HEIGHT + self.ground_offset and self.rect.bottom >= GROUND_HEIGHT + self.ground_offset:
            try:
                pg.event.post(pg.event.Event(LAND_EVENT, {'x': self.rect.centerx, 'y': self.rect.bottom}))
            except Exception:
                pass

    def tick_status(self) -> None:
        """更新惩罚、滑行与超级跳跃特效计时。"""
        if self.penalty_timer > 0:
            self.penalty_timer -= 1
        if self.super_jump_effect_timer > 0:
            self.super_jump_effect_timer -= 1
        if getattr(self, 'damage_timer', 0) > 0:
            self.damage_timer -= 1
        if self.slide_cooldown > 0:
            self.slide_cooldown -= 1
            
        # 更新滑行状态
        if self.is_sliding:
            self.slide_timer -= 1
            if self.slide_timer <= 0:
                self.is_sliding = False
                # 恢复碰撞箱高度，保持底部在地面
                self.rect.height = self.char_height
                self.rect.bottom = GROUND_HEIGHT + self.ground_offset

    def animation(self) -> None:
        """根据当前状态播放相应动画。"""
        self.anim_index += 0.15
        
        # 保存当前底部位置
        old_bottom = self.rect.bottom
        
        # 滑行状态
        if self.is_sliding:
            if self.anim_index >= len(self.slide_frames):
                self.anim_index = 0
            self.image = self.slide_frames[int(self.anim_index)]
        # 跳跃状态
        elif self.rect.bottom < GROUND_HEIGHT:
            if self.anim_index >= len(self.jump_frames):
                self.anim_index = len(self.jump_frames) - 1  # 停留在最后一帧
            self.image = self.jump_frames[int(self.anim_index)]
        # 地面跑步状态
        else:
            if self.anim_index >= len(self.run_frames):
                self.anim_index = 0
            self.image = self.run_frames[int(self.anim_index)]
        
        # 恢复底部位置，确保角色始终站在地面上
        self.rect = self.image.get_rect(midbottom=(self.rect.centerx, old_bottom))
        
        # 更新站立图像（用于开始界面）
        self.cat_stand = pg.transform.scale(
            self.idle_frames[int(self.anim_index) % len(self.idle_frames)],
            (self.char_width * 2, self.char_height * 2)
        )

    def update(self) -> None:
        self.handle_gravity()
        self.tick_status()
        self.animation()

