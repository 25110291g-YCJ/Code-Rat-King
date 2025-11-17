import pygame as pg
from settings import *


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
        if getattr(self.game, 'shield_active', False) and getattr(self.game, 'shield_timer', 0) > 0 or self.shield_badge_alpha > 0.01:
            try:
                badge_w, badge_h = 100, 28
                badge_x = x + HEALTH_BAR_WIDTH - badge_w
                badge_y = y + HEALTH_BAR_HEIGHT + 8
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
                    self.game.screen.blit(txt, (x + HEALTH_BAR_WIDTH - 120, y + HEALTH_BAR_HEIGHT + 8))
                except Exception:
                    pass
