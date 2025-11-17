import pygame as pg
from settings import *


class Cat(pg.sprite.Sprite):
    """游戏中猫咪精灵的类，负责处理跳跃、动画与惩罚状态。"""

    def __init__(self) -> None:
        super().__init__()
        self.gravity = 0
        self.cat_index = 0
        self.penalty_timer = 0
        # 碰撞无敌计时器，避免多帧重复扣血
        self.damage_timer = 0
        self.super_jump_ready = False
        self.super_jump_effect_timer = 0
        # 新规则：每成功触发三次跳跃后，下一次跳跃为超级跳跃
        # jumps_since_charge: 记录自上次超级跳后或重置后成功跳跃次数（只在实际起跳时累加）
        self.jumps_since_charge = 0
        # next_jump_super: 标志下一次起跳是否为超级跳
        self.next_jump_super = False
        # 用于追踪上一帧是否在空中，便于检测着陆事件
        self.was_in_air = False

        # 预先加载站立姿势，供开始界面使用
        cat_image = pg.image.load(CAT_STAND).convert_alpha()
        self.cat_stand = pg.transform.scale(cat_image, (CAT_WIDTH * 2, CAT_HEIGHT * 2))
        # 使用可配置的起始 X（默认向左偏移），以便在屏幕偏左区域展示角色
        self.cat_stand_rect = self.cat_stand.get_rect(center=(CAT_START_X, HEIGHT // 2))

        # 行走动画
        self.cat_walk = []
        for frame in CAT_WALK:
            walk_image = pg.image.load(frame).convert_alpha()
            walk_image = pg.transform.scale(walk_image, (CAT_WIDTH, CAT_HEIGHT))
            self.cat_walk.append(walk_image)
        self.image = self.cat_walk[self.cat_index]
        # 初始位置使用 CAT_START_X（便于调整并保持在地面）
        self.rect = self.image.get_rect(midbottom=(CAT_START_X, GROUND_HEIGHT))

        # 跳跃动画
        self.cat_jump = []
        for frame in CAT_JUMP:
            jump_image = pg.image.load(frame).convert_alpha()
            jump_image = pg.transform.scale(jump_image, (CAT_WIDTH, CAT_HEIGHT))
            self.cat_jump.append(jump_image)

        self.jump_sound = pg.mixer.Sound(JUMP_SOUND)

    def start_jump(self) -> None:
        """在收到正确打字事件时尝试起跳。"""
        if self.rect.bottom >= GROUND_HEIGHT and self.penalty_timer <= 0:
            self.cat_index = 0
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

    def apply_penalty(self) -> None:
        """触发惩罚状态，短时间内禁止再次跳跃。"""
        self.penalty_timer = PENALTY_LOCK_FRAMES
        if self.rect.bottom <= GROUND_HEIGHT:
            self.gravity = abs(self.gravity)

    def enable_super_jump(self) -> None:
        """激活超级跳跃奖励。"""
        # 通过事件触发的超级跳也作为下一次可用的超级跳（与基于跳跃计数的规则一致）
        self.super_jump_ready = True
        self.next_jump_super = True
        self.super_jump_effect_timer = SUPER_JUMP_EFFECT_FRAMES

    def handle_gravity(self) -> None:
        """根据重力效果更新猫咪的垂直位置。"""
        prev_bottom = self.rect.bottom
        if self.rect.bottom < GROUND_HEIGHT:
            self.gravity += 1
        else:
            self.rect.bottom = GROUND_HEIGHT
            self.gravity = 0
        self.rect.y += self.gravity

        # 如果上一帧在空中而本帧着地，则触发着陆事件以生成尘土粒子
        if prev_bottom < GROUND_HEIGHT and self.rect.bottom >= GROUND_HEIGHT:
            try:
                pg.event.post(pg.event.Event(LAND_EVENT, {'x': self.rect.centerx, 'y': self.rect.bottom}))
            except Exception:
                pass

    def tick_status(self) -> None:
        """更新惩罚与超级跳跃特效计时。"""
        if self.penalty_timer > 0:
            self.penalty_timer -= 1
        if self.super_jump_effect_timer > 0:
            self.super_jump_effect_timer -= 1
        if getattr(self, 'damage_timer', 0) > 0:
            self.damage_timer -= 1

    def animation(self) -> None:
        """根据当前状态播放行走或跳跃动画。"""
        self.cat_index += 0.2
        if self.rect.bottom < GROUND_HEIGHT:
            if self.cat_index >= len(self.cat_jump):
                self.cat_index = 0
            self.image = self.cat_jump[int(self.cat_index)]
        else:
            if self.cat_index >= len(self.cat_walk):
                self.cat_index = 0
            self.image = self.cat_walk[int(self.cat_index)]

    def update(self) -> None:
        self.handle_gravity()
        self.tick_status()
        self.animation()
