import pygame as pg
from settings import *
import settings


class HUD:
    """封装 HUD 绘制相关的逻辑，供 Game 复用。"""

    def __init__(self, game) -> None:
        self.game = game
        # 字体
        try:
            self.hud_font = pg.font.Font('assets/font/Purrfect.ttf', 28)
            self.hud_small_font = pg.font.Font('assets/font/Purrfect.ttf', 20)
        except Exception:
            # 退回到 pygame 默认字体
            self.hud_font = pg.font.SysFont(None, 28)
            self.hud_small_font = pg.font.SysFont(None, 20)
        # 平滑显示状态（用于动画）
        # 当前显示的血量（可为小数以实现平滑过渡）
        self.displayed_health = float(getattr(self.game, 'health', 0))
        # 当前显示的分数（平滑过渡）
        self.displayed_score = 0.0
        # 徽章透明度（0.0 - 1.0）
        self.super_badge_alpha = 0.0
        self.shield_badge_alpha = 0.0
        # 动画参数（可调）
        self.health_lerp = 0.15  # 血条插值速度
        self.score_lerp = 0.08   # 分数插值速度
        self.badge_fade_speed = 0.18  # 徽章淡入淡出速度
        # 连击弹跳（pop）动画状态
        self.last_multiplier = 1.0
        self.mult_pop_timer = 0
        self.mult_pop_duration = 12  # 弹跳持续帧数
        self.mult_pop_magnitude = 0.28  # 最大放大比例（例如 0.28 -> 最大 28% 放大）
        
        # 评级系统动画状态
        self.current_rank = 'F'
        self.current_rank_color = (100, 100, 100)
        self.rank_scale = 1.0  # 评级字母缩放比例
        self.rank_pulse_timer = 0  # 脉冲动画计时器
        self.rank_glow_alpha = 0.0  # 光晕透明度
        self.rank_bounce_offset = 0  # 持续跳动偏移量
        self.rank_bounce_phase = 0  # 跳动动画相位
        self.rank_rotation = 0  # 旋转角度
        self.rank_breath_phase = 0  # 呼吸光效相位

    def update(self) -> None:
        """每帧更新内部动画状态，Game 应在每帧调用 hud.update()。"""
        try:
            target_health = float(getattr(self.game, 'health', 0))
            # 简单线性插值（LERP）
            self.displayed_health += (target_health - self.displayed_health) * self.health_lerp
        except Exception:
            pass
        # score 平滑将通过 display_score() 在绘制时更新（避免跨模块对 text_target 的直接访问）
        # 徽章 alpha 处理
        try:
            cat_group = getattr(self.game, 'cat_group', None)
            cat_sprite = getattr(cat_group, 'sprite', None) if cat_group is not None else None
            target_super = 1.0 if ((cat_sprite and getattr(cat_sprite, 'super_jump_ready', False)) or self.game.super_jump_notice_timer > 0) else 0.0
            self.super_badge_alpha += (target_super - self.super_badge_alpha) * self.badge_fade_speed
        except Exception:
            pass
        try:
            target_shield = 1.0 if (getattr(self.game, 'shield_active', False) and getattr(self.game, 'shield_timer', 0) > 0) else 0.0
            self.shield_badge_alpha += (target_shield - self.shield_badge_alpha) * self.badge_fade_speed
        except Exception:
            pass
        # 更新连击弹跳计时器
        try:
            if self.mult_pop_timer > 0:
                self.mult_pop_timer -= 1
        except Exception:
            pass

    def display_score(self, score: int) -> None:
        # 在每次绘制分数时将 displayed_score 朝当前实际分数平滑插值
        try:
            self.displayed_score += (float(score) - self.displayed_score) * self.score_lerp
        except Exception:
            pass
        score_val = int(round(self.displayed_score))
        score_text = SCORE_FONT.render(f'Score: {score_val}', False, 'white')
        # 基础文本矩形备用（用于在缩放失败时确定倍率位置）
        base_rect = score_text.get_rect(right=WIDTH - 40, top=30)

        # 读取当前倍率（若存在），并在倍率上升时触发弹跳动画
        mult = 1.0
        try:
            tt = getattr(self.game, 'text_target', None)
            if tt and getattr(tt, 'sprite', None):
                try:
                    mult = tt.sprite.combo_multiplier()
                except Exception:
                    mult = 1.0
        except Exception:
            mult = 1.0

        # 若倍率上升则触发 pop 动画
        try:
            if mult > self.last_multiplier + 1e-6:
                self.mult_pop_timer = self.mult_pop_duration
        except Exception:
            pass
        # 始终记录当前倍率
        try:
            self.last_multiplier = mult
        except Exception:
            pass

        # 计算当前弹跳缩放（ease-out 曲线）
        scale = 1.0
        try:
            if self.mult_pop_timer > 0:
                progress = (self.mult_pop_duration - self.mult_pop_timer) / max(1, self.mult_pop_duration)
                # ease out (quadratic)
                ease = progress * (2 - progress)
                scale = 1.0 + self.mult_pop_magnitude * ease
        except Exception:
            scale = 1.0

        # 缩放并绘制分数，使右对齐与顶部对齐尽量保持一致
        try:
            ow, oh = score_text.get_size()
            nw = max(1, int(ow * scale))
            nh = max(1, int(oh * scale))
            scaled_score = pg.transform.smoothscale(score_text, (nw, nh))
            srect = scaled_score.get_rect()
            srect.right = WIDTH - 40
            # 在垂直方向上略微上移以突出弹跳效果
            srect.top = 30 - (nh - oh) // 2
            self.game.screen.blit(scaled_score, srect)
        except Exception:
            # 保证 srect 在后续倍率定位中始终可用
            srect = base_rect
            self.game.screen.blit(score_text, base_rect)
        # 若存在连击倍数（>1.0），在分数旁显示小号倍率文本
        # 绘制倍率文本（若大于 1.0），并对其应用与分数类似的弹跳缩放（但幅度稍小）
        try:
            # 若存在连击倍率（即存在 text_target），总是绘制倍率（便于调试）；当倍率=1.0 时使用较暗颜色
            if mult is not None:
                color = 'gold' if mult > 1.0 else (180, 180, 180)
                mult_text = self.hud_small_font.render(f'x{mult:.1f}', False, color)
                ow2, oh2 = mult_text.get_size()
                # multiplier 使用稍小的弹跳倍数
                mscl = 1.0
                if self.mult_pop_timer > 0:
                    try:
                        progress = (self.mult_pop_duration - self.mult_pop_timer) / max(1, self.mult_pop_duration)
                        ease = progress * (2 - progress)
                        mscl = 1.0 + (self.mult_pop_magnitude * 0.6) * ease
                    except Exception:
                        mscl = 1.0
                nw2 = max(1, int(ow2 * mscl))
                nh2 = max(1, int(oh2 * mscl))
                scaled_mult = pg.transform.smoothscale(mult_text, (nw2, nh2))
                mrect = scaled_mult.get_rect()
                # place to the right of scaled score
                try:
                    # use srect from scaled score if available
                    mrect.left = srect.right + 6
                    mrect.top = srect.top + (srect.height - nh2) // 2
                except Exception:
                    # fallback to top-right of screen
                    base_rect = score_text.get_rect(right=WIDTH - 40, top=30)
                    mrect.left = base_rect.right + 6
                    mrect.top = base_rect.top + 10
                self.game.screen.blit(scaled_mult, mrect)
        except Exception:
            pass

    def display_distance(self) -> None:
        # 保留占位以兼容调用；目前不显示距离
        return

    def display_rank(self, score: int) -> None:
        """显示动态评级UI，位于屏幕左侧中间，简洁版（无遮罩、无扫光）。
        
        Args:
            score: 当前分数
        """
        try:
            import math
            import random
            
            # 获取评级
            rank, color = self.game.get_rank(score)
            
            # 检测评级是否变化，触发强烈动画
            if rank != self.current_rank:
                self.current_rank = rank
                self.current_rank_color = color
                self.rank_scale = 2.2  # 升级时超大放大
                self.rank_pulse_timer = 60  # 持续60帧
                self.rank_glow_alpha = 1.0
            
            # 更新升级动画状态
            if self.rank_scale > 1.0:
                self.rank_scale -= 0.02
                self.rank_scale = max(1.0, self.rank_scale)
            
            if self.rank_pulse_timer > 0:
                self.rank_pulse_timer -= 1
                # 脉冲效果：光晕透明度随时间衰减
                self.rank_glow_alpha = self.rank_pulse_timer / 60.0
            else:
                self.rank_glow_alpha = 0.0
            
            # 持续跳动动画（基于正弦波）
            self.rank_bounce_phase += 0.08
            bounce_scale = 1.0 + math.sin(self.rank_bounce_phase) * 0.08
            bounce_offset = math.sin(self.rank_bounce_phase * 1.5) * 3
            
            # 轻微旋转动画（±5度）
            self.rank_rotation = math.sin(self.rank_bounce_phase * 0.7) * 5
            
            # 呼吸光效相位（慢速）
            self.rank_breath_phase += 0.04
            breath_intensity = (math.sin(self.rank_breath_phase) + 1) * 0.5  # 0-1
            
            # 创建评级字体（超大号）
            try:
                rank_font = pg.font.Font('assets/font/Purrfect.ttf', 120)
            except Exception:
                rank_font = pg.font.SysFont(None, 120)
            
            # 渲染评级字母
            rank_text = rank_font.render(rank, True, self.current_rank_color)
            
            # 应用旋转
            rotated_text = pg.transform.rotate(rank_text, self.rank_rotation)
            original_w, original_h = rotated_text.get_size()
            
            # 应用综合缩放（升级缩放 × 持续跳动缩放）
            total_scale = self.rank_scale * bounce_scale
            scaled_w = max(1, int(original_w * total_scale))
            scaled_h = max(1, int(original_h * total_scale))
            scaled_rank = pg.transform.smoothscale(rotated_text, (scaled_w, scaled_h))
            
            # 位置：屏幕左侧中间（加上跳动偏移）
            rank_x = 100
            rank_y = HEIGHT // 2 + bounce_offset
            rank_rect = scaled_rank.get_rect(center=(rank_x, rank_y))
            
            # === 1. 呼吸光效（背景最底层）===
            breath_alpha = int(breath_intensity * 80) + 20  # 20-100
            breath_glow_size = max(scaled_w, scaled_h) + 60
            breath_surface = pg.Surface((breath_glow_size, breath_glow_size), pg.SRCALPHA)
            
            # 绘制柔和的呼吸光晕
            for i in range(4):
                radius = breath_glow_size // 2 - i * 12
                alpha = max(0, breath_alpha - i * 20)
                pg.draw.circle(
                    breath_surface,
                    (*self.current_rank_color, alpha),
                    (breath_glow_size // 2, breath_glow_size // 2),
                    radius
                )
            
            breath_rect = breath_surface.get_rect(center=(rank_x, rank_y))
            self.game.screen.blit(breath_surface, breath_rect)

            # === 1.5 放射状光芒 (God Rays) ===
            # 仅在 A 和 S 级显示，增加神圣感
            if rank in ['S', 'A']:
                ray_surface = pg.Surface((breath_glow_size * 2, breath_glow_size * 2), pg.SRCALPHA)
                ray_center = (breath_glow_size, breath_glow_size)
                ray_count = 12
                # 随时间缓慢旋转
                ray_angle_offset = self.rank_breath_phase * 0.5
                
                for i in range(ray_count):
                    angle = (i / ray_count) * math.pi * 2 + ray_angle_offset
                    # 扇形光束
                    ray_length = breath_glow_size
                    ray_width = math.pi / ray_count * 0.5
                    
                    # 计算三角形顶点
                    p1 = ray_center
                    p2 = (
                        ray_center[0] + math.cos(angle - ray_width) * ray_length,
                        ray_center[1] + math.sin(angle - ray_width) * ray_length
                    )
                    p3 = (
                        ray_center[0] + math.cos(angle + ray_width) * ray_length,
                        ray_center[1] + math.sin(angle + ray_width) * ray_length
                    )
                    
                    # 绘制半透明光束
                    ray_alpha = int(40 * breath_intensity)  # 随呼吸闪烁
                    pg.draw.polygon(ray_surface, (*self.current_rank_color, ray_alpha), [p1, p2, p3])
                
                ray_rect = ray_surface.get_rect(center=(rank_x, rank_y))
                self.game.screen.blit(ray_surface, ray_rect)
            
            # === 2. 升级光晕效果 ===
            if self.rank_glow_alpha > 0.1:
                glow_size = max(scaled_w, scaled_h) + 50
                glow_surface = pg.Surface((glow_size, glow_size), pg.SRCALPHA)
                glow_alpha = int(self.rank_glow_alpha * 150)
                
                # 多层爆发光晕
                for i in range(4):
                    radius = int(glow_size // 2 - i * 8)
                    alpha = max(0, glow_alpha - i * 35)
                    pg.draw.circle(
                        glow_surface,
                        (*self.current_rank_color, alpha),
                        (glow_size // 2, glow_size // 2),
                        radius
                    )
                
                glow_rect = glow_surface.get_rect(center=(rank_x, rank_y))
                self.game.screen.blit(glow_surface, glow_rect)
            
            # === 3. 评级字母主体（直接绘制，无背景框）===
            # 添加阴影增加立体感
            shadow_offset = 4
            shadow_text = rank_font.render(rank, True, (0, 0, 0))
            shadow_rotated = pg.transform.rotate(shadow_text, self.rank_rotation)
            shadow_scaled = pg.transform.smoothscale(shadow_rotated, (scaled_w, scaled_h))
            shadow_rect = shadow_scaled.get_rect(center=(rank_x + shadow_offset, rank_y + shadow_offset))
            
            # 绘制阴影
            shadow_surface = pg.Surface(shadow_scaled.get_size(), pg.SRCALPHA)
            shadow_surface.blit(shadow_scaled, (0, 0))
            shadow_surface.set_alpha(100) # 半透明阴影
            self.game.screen.blit(shadow_surface, shadow_rect)

            # 绘制主体
            self.game.screen.blit(scaled_rank, rank_rect)
            
            # === 3.5 粒子特效 ===
            # 随机生成上升粒子
            if random.random() < 0.3: # 30%概率每帧生成
                if not hasattr(self, 'rank_particles'):
                    self.rank_particles = []
                
                p_x = rank_x + random.randint(-scaled_w//2, scaled_w//2)
                p_y = rank_y + random.randint(-scaled_h//2, scaled_h//2)
                self.rank_particles.append({
                    'x': p_x, 'y': p_y,
                    'vx': random.uniform(-0.5, 0.5), 'vy': random.uniform(-2, -0.5),
                    'life': random.randint(20, 40), 'max_life': 40,
                    'size': random.randint(2, 5)
                })
            
            # 更新和绘制粒子
            if hasattr(self, 'rank_particles'):
                for p in self.rank_particles[:]:
                    p['x'] += p['vx']
                    p['y'] += p['vy']
                    p['life'] -= 1
                    if p['life'] <= 0:
                        self.rank_particles.remove(p)
                        continue
                    
                    # 粒子绘制
                    alpha = int((p['life'] / p['max_life']) * 255)
                    particle_surf = pg.Surface((p['size']*2, p['size']*2), pg.SRCALPHA)
                    pg.draw.circle(particle_surf, (*self.current_rank_color, alpha), (p['size'], p['size']), p['size'])
                    self.game.screen.blit(particle_surf, (p['x'] - p['size'], p['y'] - p['size']))

            # === 4. 星级装饰 ===
            star_mapping = {'S': 5, 'A': 4, 'B': 3, 'C': 2, 'D': 1, 'E': 1, 'F': 0}
            star_count = star_mapping.get(rank, 0)
            
            if star_count > 0:
                star_size = 12
                star_spacing = 25
                star_y = rank_rect.top - 40
                
                # 计算起始位置（居中）
                total_width = (star_count - 1) * star_spacing
                start_x = rank_x - total_width // 2
                
                for i in range(star_count):
                    star_x = start_x + i * star_spacing
                    
                    # 星星也有轻微跳动（相位错开）
                    star_bounce = math.sin(self.rank_bounce_phase + i * 0.5) * 2
                    star_pos_y = star_y + star_bounce
                    
                    # 绘制星星（五角星）
                    self._draw_star(star_x, star_pos_y, star_size, 'gold')
            
            # === 5. RANK标签（简化版，无背景框）===
            try:
                label_font = pg.font.Font('assets/font/Purrfect.ttf', 30)
            except Exception:
                label_font = pg.font.SysFont(None, 30)
            
            label_text = label_font.render('RANK', True, (230, 230, 230))
            label_rect = label_text.get_rect(centerx=rank_x, bottom=rank_rect.top - (50 if star_count > 0 else 15))
            
            # 直接绘制标签，不要背景
            self.game.screen.blit(label_text, label_rect)
            
        except Exception as e:
            # 静默失败，避免破坏游戏
            pass
    
    def _draw_star(self, x, y, size, color):
        """绘制五角星"""
        try:
            import math
            points = []
            for i in range(5):
                angle = math.pi * 2 * i / 5 - math.pi / 2
                outer_x = x + size * math.cos(angle)
                outer_y = y + size * math.sin(angle)
                points.append((outer_x, outer_y))
                
                # 内角
                angle_inner = angle + math.pi / 5
                inner_x = x + size * 0.4 * math.cos(angle_inner)
                inner_y = y + size * 0.4 * math.sin(angle_inner)
                points.append((inner_x, inner_y))
            
            # 绘制填充星星
            pg.draw.polygon(self.game.screen, color, points)
            # 绘制星星外轮廓
            pg.draw.polygon(self.game.screen, 'orange', points, 2)
        except Exception:
            # 失败时用圆形代替
            pg.draw.circle(self.game.screen, color, (int(x), int(y)), size // 2)

    def draw_health_bar(self) -> None:
        x, y = HEALTH_BAR_POS
        w = HEALTH_BAR_WIDTH
        h = HEALTH_BAR_HEIGHT
        bg_rect = pg.Rect(x, y, w, h)
        pg.draw.rect(self.game.screen, HEALTH_BAR_BG, bg_rect)
        # 使用平滑过渡的血量显示以获得动画效果
        ratio = max(0, min(1.0, self.displayed_health / MAX_HEALTH))
        fg_rect = pg.Rect(x, y, int(w * ratio), h)
        pg.draw.rect(self.game.screen, HEALTH_BAR_COLOR, fg_rect)
        pg.draw.rect(self.game.screen, 'black', bg_rect, 3)
        # 文本也使用整数化的平滑值
        text = self.hud_font.render(f'HP: {int(round(self.displayed_health))}/{MAX_HEALTH}', False, 'white')
        text_rect = text.get_rect(midleft=(x + w + 12, y + h // 2))
        self.game.screen.blit(text, text_rect)

    def draw_damage_popups(self) -> None:
        for popup in (self.game.damage_popups[:] if hasattr(self.game, 'damage_popups') else []):
            try:
                txt = self.hud_font.render(popup.get('text', '-1 HP'), False, 'salmon')
                txt_rect = txt.get_rect(center=(popup['x'], popup['y']))
                self.game.screen.blit(txt, txt_rect)
                popup['y'] -= 1
                popup['timer'] -= 1
                if popup['timer'] <= 0:
                    try:
                        self.game.damage_popups.remove(popup)
                    except Exception:
                        pass
            except Exception:
                try:
                    self.game.damage_popups.remove(popup)
                except Exception:
                    pass

    def draw_super_jump_notice(self) -> None:
        # 通过 Game 暴露的 cat_group 读取猫咪状态（避免跨模块全局依赖）
        cat_group = getattr(self.game, 'cat_group', None)
        cat_sprite = getattr(cat_group, 'sprite', None) if cat_group is not None else None
        show_notice = ((cat_sprite and getattr(cat_sprite, 'super_jump_ready', False)) or self.game.super_jump_notice_timer > 0)
        # 缓动 alpha：若 alpha 非显著（接近 0）可略过绘制
        if not show_notice and self.super_badge_alpha <= 0.01:
            return
        x, y = HEALTH_BAR_POS
        badge_w, badge_h = 160, 34
        badge_x = x
        badge_y = y + HEALTH_BAR_HEIGHT + 8
        try:
            badge = pg.Surface((badge_w, badge_h), pg.SRCALPHA)
            # 将 alpha 合成到整体 surface
            base_color = (20, 20, 20, int(180 * max(0.0, min(1.0, self.super_badge_alpha))))
            badge.fill(base_color)
            pg.draw.rect(badge, SUPER_JUMP_TEXT_COLOR, badge.get_rect(), 2)
            text_surf = self.hud_small_font.render('SUPER JUMP', False, 'white')
            txt_rect = text_surf.get_rect(center=(badge_w // 2, badge_h // 2))
            badge.blit(text_surf, txt_rect)
            # 最终 blit
            try:
                self.game.screen.blit(badge, (badge_x, badge_y))
            except Exception:
                pass
        except Exception:
            notice = self.hud_small_font.render('SUPER JUMP', False, SUPER_JUMP_TEXT_COLOR)
            notice_rect = notice.get_rect(left=x, top=y + HEALTH_BAR_HEIGHT + 8)
            self.game.screen.blit(notice, notice_rect)
        if self.game.super_jump_notice_timer > 0:
            self.game.super_jump_notice_timer -= 1

    def draw_active_effects(self) -> None:
        x, y = HEALTH_BAR_POS
        badge_y = y + HEALTH_BAR_HEIGHT + 8
        
        # 护盾显示
        if getattr(self.game, 'shield_active', False) and getattr(self.game, 'shield_timer', 0) > 0 or self.shield_badge_alpha > 0.01:
            try:
                badge_w, badge_h = 100, 28
                badge_x = x + HEALTH_BAR_WIDTH - badge_w
                badge = pg.Surface((badge_w, badge_h), pg.SRCALPHA)
                base_color = (10, 60, 140, int(180 * max(0.0, min(1.0, self.shield_badge_alpha))))
                badge.fill(base_color)
                pg.draw.rect(badge, (180, 220, 255), badge.get_rect(), 2)
                secs = max(0, self.game.shield_timer // FPS)
                txt = self.hud_small_font.render(f'SHIELD {secs}s', False, 'white')
                badge.blit(txt, txt.get_rect(center=(badge_w // 2, badge_h // 2)))
                try:
                    self.game.screen.blit(badge, (badge_x, badge_y))
                except Exception:
                    pass
            except Exception:
                try:
                    txt = self.hud_small_font.render(f'SHIELD {self.game.shield_timer//FPS}s', False, 'white')
                    self.game.screen.blit(txt, (x + HEALTH_BAR_WIDTH - 120, badge_y))
                except Exception:
                    pass
        
        # 滑行冷却显示
        try:
            cat_group = getattr(self.game, 'cat_group', None)
            cat_sprite = getattr(cat_group, 'sprite', None) if cat_group is not None else None
            if cat_sprite and hasattr(cat_sprite, 'slide_cooldown'):
                cooldown = cat_sprite.slide_cooldown
                max_cooldown = getattr(settings, 'SLIDE_COOLDOWN', 90)
                
                # 只在冷却中或滑行中显示
                if cooldown > 0 or getattr(cat_sprite, 'is_sliding', False):
                    badge_w, badge_h = 120, 28
                    badge_x = x + HEALTH_BAR_WIDTH - badge_w - 110  # 在护盾左侧
                    
                    badge = pg.Surface((badge_w, badge_h), pg.SRCALPHA)
                    
                    if getattr(cat_sprite, 'is_sliding', False):
                        # 滑行中：绿色提示
                        badge.fill((20, 140, 60, 180))
                        pg.draw.rect(badge, (180, 255, 180), badge.get_rect(), 2)
                        txt = self.hud_small_font.render('SLIDING', False, 'white')
                    elif cooldown > 0:
                        # 冷却中：显示倒计时
                        badge.fill((60, 60, 60, 180))
                        pg.draw.rect(badge, (150, 150, 150), badge.get_rect(), 2)
                        secs = cooldown / FPS
                        txt = self.hud_small_font.render(f'SLIDE {secs:.1f}s', False, 'lightgray')
                        
                        # 绘制冷却进度条
                        progress = 1.0 - (cooldown / max_cooldown)
                        bar_w = int((badge_w - 8) * progress)
                        bar_rect = pg.Rect(4, badge_h - 6, bar_w, 2)
                        pg.draw.rect(badge, (100, 200, 255), bar_rect)
                    else:
                        return
                    
                    badge.blit(txt, txt.get_rect(center=(badge_w // 2, badge_h // 2 - 2)))
                    self.game.screen.blit(badge, (badge_x, badge_y))
        except Exception:
            pass

    def draw_slide_hint(self) -> None:
        """在HUD中显示滑行技能的按键提示（游戏进行时显示）"""
        # 只在游戏活动状态下显示
        if not getattr(self.game, 'game_active', False):
            return
        
        try:
            cat_group = getattr(self.game, 'cat_group', None)
            cat_sprite = getattr(cat_group, 'sprite', None) if cat_group is not None else None
            
            if cat_sprite and hasattr(cat_sprite, 'slide_cooldown'):
                cooldown = cat_sprite.slide_cooldown
                is_sliding = getattr(cat_sprite, 'is_sliding', False)
                
                # 如果正在滑行或冷却中，不显示提示（因为已经有状态显示）
                if is_sliding or cooldown > 0:
                    return
                
                # 显示按键提示：左下角
                hint_x = 40
                hint_y = HEIGHT - 60
                
                # 创建半透明背景
                hint_w, hint_h = 160, 32
                hint_bg = pg.Surface((hint_w, hint_h), pg.SRCALPHA)
                hint_bg.fill((40, 40, 40, 150))
                pg.draw.rect(hint_bg, (120, 120, 120), hint_bg.get_rect(), 2)
                
                # 绘制文本：左Ctrl = 滑行
                txt = self.hud_small_font.render('L-Ctrl = SLIDE', False, 'lightgreen')
                hint_bg.blit(txt, txt.get_rect(center=(hint_w // 2, hint_h // 2)))
                
                self.game.screen.blit(hint_bg, (hint_x, hint_y))
        except Exception:
            pass
