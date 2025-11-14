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

    def display_score(self, score: int) -> None:
        score_text = SCORE_FONT.render(f'Score: {score}', False, 'white')
        score_rect = score_text.get_rect(right=WIDTH - 40, top=30)
        self.game.screen.blit(score_text, score_rect)

    def display_distance(self) -> None:
        # 保留占位以兼容调用；目前不显示距离
        return

    def draw_health_bar(self) -> None:
        x, y = HEALTH_BAR_POS
        w = HEALTH_BAR_WIDTH
        h = HEALTH_BAR_HEIGHT
        bg_rect = pg.Rect(x, y, w, h)
        pg.draw.rect(self.game.screen, HEALTH_BAR_BG, bg_rect)
        ratio = max(0, min(1.0, self.game.health / MAX_HEALTH))
        fg_rect = pg.Rect(x, y, int(w * ratio), h)
        pg.draw.rect(self.game.screen, HEALTH_BAR_COLOR, fg_rect)
        pg.draw.rect(self.game.screen, 'black', bg_rect, 3)
        text = self.hud_font.render(f'HP: {self.game.health}/{MAX_HEALTH}', False, 'white')
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
        if not show_notice:
            return
        x, y = HEALTH_BAR_POS
        badge_w, badge_h = 160, 34
        badge_x = x
        badge_y = y + HEALTH_BAR_HEIGHT + 8
        try:
            badge = pg.Surface((badge_w, badge_h), pg.SRCALPHA)
            badge.fill((20, 20, 20, 180))
            pg.draw.rect(badge, SUPER_JUMP_TEXT_COLOR, badge.get_rect(), 2)
            text_surf = self.hud_small_font.render('SUPER JUMP', False, 'white')
            txt_rect = text_surf.get_rect(center=(badge_w // 2, badge_h // 2))
            badge.blit(text_surf, txt_rect)
            self.game.screen.blit(badge, (badge_x, badge_y))
        except Exception:
            notice = self.hud_small_font.render('SUPER JUMP', False, SUPER_JUMP_TEXT_COLOR)
            notice_rect = notice.get_rect(left=x, top=y + HEALTH_BAR_HEIGHT + 8)
            self.game.screen.blit(notice, notice_rect)
        if self.game.super_jump_notice_timer > 0:
            self.game.super_jump_notice_timer -= 1

    def draw_active_effects(self) -> None:
        x, y = HEALTH_BAR_POS
        if getattr(self.game, 'shield_active', False) and getattr(self.game, 'shield_timer', 0) > 0:
            try:
                badge_w, badge_h = 100, 28
                badge_x = x + HEALTH_BAR_WIDTH - badge_w
                badge_y = y + HEALTH_BAR_HEIGHT + 8
                badge = pg.Surface((badge_w, badge_h), pg.SRCALPHA)
                badge.fill((10, 60, 140, 180))
                pg.draw.rect(badge, (180, 220, 255), badge.get_rect(), 2)
                secs = max(0, self.game.shield_timer // FPS)
                txt = self.hud_small_font.render(f'SHIELD {secs}s', False, 'white')
                badge.blit(txt, txt.get_rect(center=(badge_w // 2, badge_h // 2)))
                self.game.screen.blit(badge, (badge_x, badge_y))
            except Exception:
                try:
                    txt = self.hud_small_font.render(f'SHIELD {self.game.shield_timer//FPS}s', False, 'white')
                    self.game.screen.blit(txt, (x + HEALTH_BAR_WIDTH - 120, y + HEALTH_BAR_HEIGHT + 8))
                except Exception:
                    pass
