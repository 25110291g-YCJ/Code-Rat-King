from random import choice, randint, random
from sys import exit

import pygame as pg

from settings import *
import settings
from hud import HUD
from player import Player
from trees import Trees
from particles import Particle, DustParticle
from items import GroundItem
from background import Background
from dog import Dog
from house import House
from text_target import TextTarget
from boss import Boss, Bullet


class Game:
    """游戏主类，负责场景渲染、事件循环、难度与音效管理。"""

    def __init__(self) -> None:
        pg.init()
        self.game_active = False
        self.clock = pg.time.Clock()
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        pg.display.set_caption('A Trip Home')

        self.flash_counter = 0
        self.current_track = 0
        self.cat_dog_collision = False
        self.penalty_flash_timer = 0
        self.super_jump_notice_timer = 0
        self.difficulty_stage = -1
        self.tree_spawn_interval = TREE_SPAWN_FREQ
        self.dog_spawn_interval = DOG_SPAWN_FREQ
        settings.CURRENT_MOVING_SPEED = MOVING_SPEED

        self.game_name = TITLE_FONT.render('A Trip Home', False, 'white')
        self.game_name_rect = self.game_name.get_rect(center=(WIDTH // 2, GAMENAME_HEIGHT))
        self.game_message = TITLE_FONT.render('Press SPACE to play', False, 'white')
        self.game_message_rect = self.game_message.get_rect(
            center=(WIDTH // 2, GAMEMESSAGE_HEIGHT)
        )

        # 背景管理（多层视差）由 Background 类负责
        try:
            self.background = Background()
        except Exception:
            # 若背景模块或资源加载失败，保留兼容的占位字段
            self.background = None

        # 关卡列表:按顺序推进。每一项为 (level_key, folder_name)
        # level_key: 用于内部标识（'sky','mine','volcano'），folder_name: assets 子目录（None 使用默认 sky+ground）
        self.levels = [
            {'key': 'sky', 'folder': None},
            {'key': 'mine', 'folder': 'Mine'},
            {'key': 'volcano', 'folder': 'Volcano'},
        ]
        self.current_level_index = 0
        # 关卡过渡提示状态
        self.show_level_transition = False
        self.level_transition_timer = 0
        self.level_transition_text = ''

        pg.mixer.music.set_volume(0.5)
        self.play_pregame_music()

        self.bark_sound = pg.mixer.Sound(BARK_SOUND)
        self.win_sound = pg.mixer.Sound(WIN_SOUND)
        # 猫受击音效（与打字命中音效分开）
        try:
            self.cat_hit_sound = pg.mixer.Sound(HIT_SOUND)
        except Exception:
            self.cat_hit_sound = None

        # HUD / 状态：血量等状态保存在实例中，字体与绘制由 hud.py 管理
        self.health = settings.MAX_HEALTH

        # Game Over 状态与音效
        self.lose_sound = pg.mixer.Sound(LOSE_SOUND)
        self.show_game_over = False
        self.show_victory = False
        self.victory_timer = 0
        self.victory_score = 0
        self.game_over_timer = 0
        self.game_over_score = 0
        # 受伤浮动文字列表，元素为 dict {'x','y','timer','text'}
        self.damage_popups = []
        # 粒子特效组与树破碎音效
        try:
            self.tree_break_sound = pg.mixer.Sound(TREE_BREAK_SOUND)
        except Exception:
            self.tree_break_sound = None
        self.particles = pg.sprite.Group()
        # 道具组
        self.items = pg.sprite.Group()
        try:
            self.item_timer = settings.ITEM_SPAWN
            pg.time.set_timer(self.item_timer, getattr(settings, 'ITEM_SPAWN_FREQ', 10000))
        except Exception:
            self.item_timer = None

        self.tree_timer = TREE_SPAWN
        self.dog_timer = DOG_SPAWN
        # 单次房屋生成：记录时间戳与已生成标志
        self.house_spawn_time_ms = None
        self.house_spawned = False
        # 护盾状态
        self.shield_active = False
        self.shield_timer = 0

        pg.time.set_timer(self.tree_timer, TREE_SPAWN_FREQ)
        pg.time.set_timer(self.dog_timer, DOG_SPAWN_FREQ)
        self._init_groups()
        # 将全局组引用回写到实例，便于 HUD/其他模块访问（避免循环导入）
        # 暴露 text_target 以便 HUD 或其他系统读取当前分数/连击信息
        self.text_target = text_target
        self.cat_group = cat
        self.trees_group = trees
        self.house_group = house
        self.dog_group = dog
        self.boss_group = boss
        self.bullets_group = bullets
        
        # Boss 状态
        self.boss_active = False  # Boss 是否激活
        self.boss_spawned = False  # Boss 是否已生成
        
        # 创建 HUD 管理器（将 HUD 逻辑放到 hud.py）
        try:
            self.hud = HUD(self)
        except Exception:
            self.hud = None

        # 屏幕抖动状态（受击时触发短暂抖动）
        # 以帧为单位的计时器、初始持续帧数以及抖动强度（像素）
        self.screen_shake_timer = 0
        self.screen_shake_duration = 0
        self.screen_shake_magnitude = 0
        

    def draw_active_effects(self) -> None:
        """绘制当前激活的持续性效果（如护盾）的 HUD 徽章与计时条。"""
        # Delegate to HUD if available, otherwise draw a small fallback badge
        if getattr(self, 'hud', None):
            try:
                return self.hud.draw_active_effects()
            except Exception:
                pass

        x, y = HEALTH_BAR_POS
        # 护盾显示在血条下方，靠右排列，避让超级跳徽章（fallback）
        if getattr(self, 'shield_active', False) and getattr(self, 'shield_timer', 0) > 0:
            try:
                badge_w, badge_h = 100, 28
                badge_x = x + HEALTH_BAR_WIDTH - badge_w
                badge_y = y + HEALTH_BAR_HEIGHT + 8
                badge = pg.Surface((badge_w, badge_h), pg.SRCALPHA)
                badge.fill((10, 60, 140, 180))
                pg.draw.rect(badge, (180, 220, 255), badge.get_rect(), 2)
                secs = max(0, self.shield_timer // FPS)
                # fallback font
                try:
                    font = pg.font.Font('assets/font/Purrfect.ttf', 18)
                except Exception:
                    font = pg.font.SysFont(None, 18)
                txt = font.render(f'SHIELD {secs}s', False, 'white')
                badge.blit(txt, txt.get_rect(center=(badge_w // 2, badge_h // 2)))
                self.screen.blit(badge, (badge_x, badge_y))
            except Exception:
                try:
                    font = pg.font.SysFont(None, 18)
                    txt = font.render(f'SHIELD {self.shield_timer//FPS}s', False, 'white')
                    self.screen.blit(txt, (x + HEALTH_BAR_WIDTH - 120, y + HEALTH_BAR_HEIGHT + 8))
                except Exception:
                    pass

    def _init_groups(self) -> None:
        global text_target, cat, trees, house, dog, boss, bullets
        text_target = pg.sprite.GroupSingle()
        text_target.add(TextTarget())
        cat = pg.sprite.GroupSingle()
        cat.add(Player())  # 使用新的Player类
        trees = pg.sprite.Group()
        house = pg.sprite.GroupSingle()
        dog = pg.sprite.Group()
        # 粒子组在这里也要存在为更新/绘制准备
        self.particles = pg.sprite.Group()
        # 道具组
        self.items = pg.sprite.Group()
        # Boss 和子弹组
        boss = pg.sprite.GroupSingle()
        bullets = pg.sprite.Group()

    def play_pregame_music(self) -> None:
        pg.mixer.music.stop()
        pg.mixer.music.load(PREGAME_MUSIC)
        pg.mixer.music.set_volume(0.5)
        pg.mixer.music.play(loops=-1)
        pg.mixer.music.set_endevent()

    def create_dust(self, x: int, y: int, count: int | None = None) -> None:
        """在指定位置生成若干尘土粒子（用于着陆效果）。"""
        if count is None:
            count = getattr(settings, 'DUST_PARTICLE_COUNT', 8)
        for _ in range(count):
            color = choice(getattr(settings, 'DUST_PARTICLE_COLORS', [(200, 180, 140)]))
            dx = randint(-10, 10)
            dy = randint(-4, 4)
            p = DustParticle(x + dx, y + dy, color)
            try:
                self.particles.add(p)
            except Exception:
                pass

    def get_rank(self, score: int) -> tuple:
        """根据分数计算评级等级和颜色。
        
        Args:
            score: 玩家得分
            
        Returns:
            tuple: (评级字母, 颜色RGB元组)
        """
        rank_thresholds = getattr(settings, 'RANK_THRESHOLDS', [
            (200, 'S', (255, 215, 0)),
            (150, 'A', (255, 100, 100)),
            (120, 'B', (100, 150, 255)),
            (80, 'C', (100, 255, 100)),
            (50, 'D', (200, 200, 200)),
            (20, 'E', (150, 150, 150)),
            (0, 'F', (100, 100, 100))
        ])
        
        for threshold, rank, color in rank_thresholds:
            if score >= threshold:
                return (rank, color)
        return ('F', (100, 100, 100))

    def display_score(self, score: int) -> None:
        if getattr(self, 'hud', None):
            return self.hud.display_score(score)
        score_text = SCORE_FONT.render(f'Score: {score}', False, 'white')
        score_rect = score_text.get_rect(right=WIDTH - 40, top=30)
        self.screen.blit(score_text, score_rect)

    def display_distance(self) -> None:
        """已移除：HUD 不再显示到终点的距离与 ETA（保留该函数以保持调用兼容）。"""
        if getattr(self, 'hud', None):
            return self.hud.display_distance()
        return

    def collision(self) -> bool:
        if not cat.sprite:
            return True

        if pg.sprite.spritecollide(cat.sprite, dog, False):
            if not self.cat_dog_collision:
                self.bark_sound.play()
                self.cat_dog_collision = True
        else:
            self.cat_dog_collision = False

        # 检测与树的碰撞：使用较小的碰撞箱比例以减少误碰
        # collide_rect_ratio 返回一个可作为 collided 回调的函数
        # 如果玩家正在滑行，降低碰撞检测高度
        if getattr(cat.sprite, 'is_sliding', False):
            # 滑行时使用更低的碰撞比例，可以躲过高处的障碍
            collide_ratio = pg.sprite.collide_rect_ratio(0.5)
        else:
            collide_ratio = pg.sprite.collide_rect_ratio(0.7)  # 0.7 可以根据需要调整（0.0-1.0）
        collided_trees = pg.sprite.spritecollide(cat.sprite, trees, False, collided=collide_ratio)
        if collided_trees:
            # 如果护盾激活，则不扣血，直接移除树并播放破碎特效
            if getattr(self, 'shield_active', False):
                try:
                    for t in collided_trees:
                        cx, cy = t.rect.centerx, t.rect.centery
                        for _ in range(settings.PARTICLE_COUNT):
                            color = choice(settings.PARTICLE_COLORS)
                            p = Particle(cx + randint(-10, 10), cy + randint(-10, 10), color)
                            self.particles.add(p)
                        try:
                            if self.tree_break_sound:
                                self.tree_break_sound.play()
                        except Exception:
                            pass
                        t.kill()
                except Exception:
                    pass
            else:
                # 只在没有无敌计时器时造成伤害
                if getattr(cat.sprite, 'damage_timer', 0) <= 0:
                    # 扣血
                    self.health -= 1
                    # 触发短暂无敌，防止多帧重复扣血
                    cat.sprite.damage_timer = settings.DAMAGE_INVULN_FRAMES
                    # 视觉反馈
                    self.penalty_flash_timer = PENALTY_FLASH_FRAMES
                    try:
                        self.lose_sound.play()
                    except Exception:
                        pass
                    # 播放受击音效（短促）
                    try:
                        if self.cat_hit_sound:
                            self.cat_hit_sound.play()
                    except Exception:
                        pass
                    # 触发短暂屏幕抖动以增强受击反馈
                    try:
                        # duration (frames), magnitude (px)
                        self.trigger_screen_shake(12, 8)
                    except Exception:
                        pass
                    
                    # 受伤浮动文字（显示在猫头上方）
                    try:
                        popup_x = cat.sprite.rect.centerx
                        popup_y = cat.sprite.rect.top - 10
                        self.damage_popups.append({
                            'x': popup_x,
                            'y': popup_y,
                            'timer': settings.DAMAGE_POPUP_FRAMES,
                            'text': '-1 HP'
                        })
                    except Exception:
                        pass
                    # 移除造成碰撞的树，并生成碎片粒子特效
                    try:
                        for t in collided_trees:
                            # 生成若干颗粒子
                            cx, cy = t.rect.centerx, t.rect.centery
                            for _ in range(settings.PARTICLE_COUNT):
                                color = choice(settings.PARTICLE_COLORS)
                                p = Particle(cx + randint(-10, 10), cy + randint(-10, 10), color)
                                self.particles.add(p)
                            # 播放树破碎音效
                            try:
                                if self.tree_break_sound:
                                    self.tree_break_sound.play()
                            except Exception:
                                pass
                            t.kill()
                    except Exception:
                        pass
                    # 若血量耗尽，进入 Game Over 状态并返回 False（结束运行）
                    if self.health <= 0:
                        # 记录分数
                        final_score = text_target.sprite.score if text_target.sprite else 0
                        self.show_game_over = True
                        self.game_over_timer = GAME_OVER_DURATION
                        self.game_over_score = final_score
                        pg.mixer.music.stop()
                        # 清理场景
                        trees.empty()
                        house.empty()
                        dog.empty()
                        try:
                            self.items.empty()
                        except Exception:
                            pass
                        return False

        collided_houses = pg.sprite.spritecollide(cat.sprite, house, False)
        for collided_house in collided_houses:
            if collided_house.rect.centerx <= cat.sprite.rect.centerx:
                # 播放到达房屋音效并短暂停顿
                try:
                    self.win_sound.play()
                except Exception:
                    pass
                pg.time.delay(DELAY_TIME)
                # 清理当前场景的实体
                trees.empty()
                house.empty()
                dog.empty()
                try:
                    self.items.empty()
                except Exception:
                    pass

                # 若存在下一关，则进入下一关并继续游戏；否则视为最终通关
                try:
                    if self.current_level_index < len(self.levels) - 1:
                        self.current_level_index += 1
                        next_level = self.levels[self.current_level_index]
                        
                        # 清空上一关的Boss子弹，避免带入新关卡
                        try:
                            bullets.empty()
                        except Exception as e:
                            print(f"Error clearing bullets: {e}")
                        
                        # 切换背景（如果 background 可用）
                        try:
                            if getattr(self, 'background', None):
                                # 使用 Background 提供的 set_level（接受关卡 key）
                                self.background.set_level(next_level['key'])
                        except Exception as e:
                            print(f"Error setting level background: {e}")
                            import traceback
                            traceback.print_exc()
                        # 触发关卡过渡提示：暂停游戏并展示文字
                        try:
                            trans_ms = int(getattr(settings, 'LEVEL_TRANSITION_MS', 2000))
                        except Exception:
                            trans_ms = 2000
                        # 设置显示文本（只显示关卡编号，如 "LEVEL 2"）
                        self.level_transition_text = f'LEVEL {self.current_level_index + 1}'
                        self.level_transition_timer = trans_ms
                        self.show_level_transition = True
                        # 在过渡期间把下一关的房屋生成时间向后偏移，确保是在过渡后再开始计时
                        try:
                            delay_ms = int(getattr(settings, 'HOUSE_FIXED_SPAWN_MS', 60000))
                        except Exception:
                            delay_ms = 60000
                        self.house_spawn_time_ms = pg.time.get_ticks() + delay_ms + trans_ms
                        self.house_spawned = False
                        return False
                    else:
                        final_score = text_target.sprite.score if text_target.sprite else 0
                        self.show_victory = True
                        self.victory_timer = GAME_OVER_DURATION
                        self.victory_score = final_score
                        pg.mixer.music.stop()
                        return False
                except Exception as e:
                    # 出现异常时回退为原有胜利逻辑，并打印错误信息
                    print(f"Critical error in level transition: {e}")
                    import traceback
                    traceback.print_exc()
                    final_score = text_target.sprite.score if text_target.sprite else 0
                    self.show_victory = True
                    self.victory_timer = GAME_OVER_DURATION
                    self.victory_score = final_score
                    pg.mixer.music.stop()
                    return False

        # 检测与道具的碰撞（拾取）
        try:
            picked = pg.sprite.spritecollide(cat.sprite, self.items, False)
            for it in picked:
                try:
                    self.apply_item_effect(it.type)
                except Exception:
                    pass
                try:
                    it.kill()
                except Exception:
                    pass
        except Exception:
            pass
        
        # 检测与 Boss 子弹的碰撞
        try:
            if self.boss_active and cat.sprite:
                hit_bullets = pg.sprite.spritecollide(cat.sprite, bullets, False)
                for bullet in hit_bullets:
                    # 判断玩家是否成功躲避
                    dodged = False
                    
                    if bullet.bullet_type == 'A':
                        # A类子弹：玩家需要滑行才能躲避
                        if getattr(cat.sprite, 'is_sliding', False):
                            dodged = True
                    elif bullet.bullet_type == 'B':
                        # B类子弹：玩家站立不动即可躲避（在空中或滑行时会被击中）
                        if not getattr(cat.sprite, 'is_sliding', False) and cat.sprite.rect.bottom >= GROUND_HEIGHT + getattr(cat.sprite, 'ground_offset', 0):
                            dodged = True
                    else:  # C类子弹
                        # C类子弹：玩家需要跳跃才能躲避
                        if cat.sprite.rect.bottom < GROUND_HEIGHT + getattr(cat.sprite, 'ground_offset', 0):
                            dodged = True
                    
                    # 移除子弹
                    bullet.kill()
                    
                    # 如果没有躲避成功且没有护盾，扣血
                    if not dodged:
                        if getattr(self, 'shield_active', False):
                            # 有护盾，不扣血但消耗护盾
                            pass
                        else:
                            # 没有护盾且没有无敌时间，扣血
                            if getattr(cat.sprite, 'damage_timer', 0) <= 0:
                                self.health -= 1
                                cat.sprite.damage_timer = settings.DAMAGE_INVULN_FRAMES
                                self.penalty_flash_timer = PENALTY_FLASH_FRAMES
                                try:
                                    self.lose_sound.play()
                                except Exception:
                                    pass
                                try:
                                    if self.cat_hit_sound:
                                        self.cat_hit_sound.play()
                                except Exception:
                                    pass
                                try:
                                    self.trigger_screen_shake(12, 8)
                                except Exception:
                                    pass
                                
                                # 受伤浮动文字
                                try:
                                    popup_x = cat.sprite.rect.centerx
                                    popup_y = cat.sprite.rect.top - 10
                                    self.damage_popups.append({
                                        'x': popup_x,
                                        'y': popup_y,
                                        'timer': settings.DAMAGE_POPUP_FRAMES,
                                        'text': '-1 HP'
                                    })
                                except Exception:
                                    pass
                                
                                # 血量耗尽 -> Game Over
                                if self.health <= 0:
                                    self.game_active = False
                                    self.show_game_over = True
                                    self.game_over_timer = GAME_OVER_DURATION
                                    self.game_over_score = text_target.sprite.score if text_target.sprite else 0
                                    pg.mixer.music.stop()
                                    trees.empty()
                                    house.empty()
                                    dog.empty()
                                    boss.empty()
                                    bullets.empty()
                                    return False
        except Exception as e:
            print(f"Error in bullet collision: {e}")
            pass
        
        return True

    def play_next_music(self) -> None:
        if not INGAME_MUSIC:
            return
        pg.mixer.music.load(INGAME_MUSIC[self.current_track])
        self.current_track = (self.current_track + 1) % len(INGAME_MUSIC)
        pg.mixer.music.set_volume(0.3)
        pg.mixer.music.play()
        pg.mixer.music.set_endevent(NEXT_MUSIC)

    def apply_item_effect(self, t: str) -> None:
        """应用道具效果：health、shield 等。"""
        try:
            if t == 'health':
                # 回复 1 点生命
                self.health = min(self.health + 1, settings.MAX_HEALTH)
                try:
                    pg.mixer.Sound(getattr(settings, 'HEALTH_SOUND', '')).play()
                except Exception:
                    pass
            elif t == 'shield':
                # 启动护盾效果（持续 SHIELD_DURATION 秒）
                dur = getattr(settings, 'SHIELD_DURATION', 3)
                self.shield_active = True
                self.shield_timer = int(dur * FPS)
                try:
                    pg.mixer.Sound(getattr(settings, 'SHIELD_SOUND', '')).play()
                except Exception:
                    pass
            elif t == 'superjump':
                # 立即授予一次超级跳（可被下一次起跳消耗）
                try:
                    if cat.sprite:
                        cat.sprite.enable_super_jump()
                        # 同步 HUD 提示计时器
                        try:
                            self.super_jump_notice_timer = SUPER_JUMP_NOTICE_FRAMES
                        except Exception:
                            pass
                        # 可选播放音效（若配置了 SUPERJUMP_SOUND）
                        try:
                            pg.mixer.Sound(getattr(settings, 'SUPERJUMP_SOUND', '')).play()
                        except Exception:
                            pass
                except Exception:
                    pass
        except Exception:
            pass

    def spawn_boss(self) -> None:
        """生成 Boss"""
        if not self.boss_spawned:
            boss.add(Boss())
            self.boss_active = True
            self.boss_spawned = True
            # 触发强烈的屏幕震动
            try:
                self.trigger_screen_shake(30, 15)
            except Exception:
                pass
            # 可选：停止树木生成
            try:
                pg.time.set_timer(self.tree_timer, 0)  # 停止树木生成
            except Exception:
                pass
            print("Boss spawned!")  # 调试信息

    def reset_run_state(self) -> None:
        self.game_active = True
        self.flash_counter = 0
        self.penalty_flash_timer = 0
        self.super_jump_notice_timer = 0
        self.difficulty_stage = -1
        settings.CURRENT_MOVING_SPEED = MOVING_SPEED
        self.tree_spawn_interval = TREE_SPAWN_FREQ
        self.house_spawn_interval = HOUSE_SPAWN_FREQ
        self.dog_spawn_interval = DOG_SPAWN_FREQ

        trees.empty()
        house.empty()
        dog.empty()
        try:
            self.items.empty()
        except Exception:
            pass
        
        # 清理 Boss 和子弹
        boss.empty()
        bullets.empty()
        
        # Boss 始终存在 - 自动生成
        try:
            boss.add(Boss())
            self.boss_active = True
            self.boss_spawned = True
        except Exception as e:
            print(f"Failed to spawn boss: {e}")
            self.boss_active = False
            self.boss_spawned = False

        if cat.sprite:
            cat.sprite.super_jump_ready = False
            cat.sprite.penalty_timer = 0
            cat.sprite.gravity = 0
            # 复位猫的位置到可配置的起始 X，并置于地面
            try:
                ground_offset = getattr(cat.sprite, 'ground_offset', 0)
                cat.sprite.rect = cat.sprite.image.get_rect(midbottom=(CAT_START_X, GROUND_HEIGHT + ground_offset))
                # 同步站立姿势的 rect（开始界面使用）
                try:
                    cat.sprite.cat_stand_rect = cat.sprite.cat_stand.get_rect(center=(CAT_START_X, HEIGHT // 2))
                except Exception:
                    pass
            except Exception:
                # 回退：仅重置底部坐标
                ground_offset = getattr(cat.sprite, 'ground_offset', 0)
                cat.sprite.rect.bottom = GROUND_HEIGHT + ground_offset

        if text_target.sprite:
            text_target.sprite.score = 0
            text_target.sprite.letter_count = 0
            text_target.sprite.combo_count = 0
            text_target.sprite.pick_new_word()

        # 重置玩家血量
        self.health = settings.MAX_HEALTH
        # 清除任何残留的受伤弹窗
        try:
            self.damage_popups.clear()
        except Exception:
            pass
        # 清除残留粒子
        try:
            self.particles.empty()
        except Exception:
            pass
        # 重置道具状态（护盾等）
        try:
            self.items.empty()
        except Exception:
            pass
        self.shield_active = False
        self.shield_timer = 0
        # 重置背景偏移（多层）
        try:
            if getattr(self, 'background', None):
                self.background.reset()
        except Exception:
            # 保持向后兼容：如果 background 不可用，回退为原行为（清空字段）
            try:
                self.sky_layers = []
            except Exception:
                pass
            try:
                self.ground_layers = []
            except Exception:
                pass

        # 重置关卡到第一关（新的运行从 sky 开始）
        try:
            self.current_level_index = 0
            if getattr(self, 'background', None):
                lvl = self.levels[self.current_level_index]
                try:
                    self.background.set_level(lvl['key'])
                except Exception:
                    pass
        except Exception:
            pass

        pg.time.set_timer(self.tree_timer, TREE_SPAWN_FREQ)
        pg.time.set_timer(self.dog_timer, DOG_SPAWN_FREQ)
        # 记录一次性房屋生成时间（相对于当前 ticks）
        try:
            delay_ms = int(getattr(settings, 'HOUSE_FIXED_SPAWN_MS', 60000))
        except Exception:
            delay_ms = 60000
        self.house_spawn_time_ms = pg.time.get_ticks() + max(0, delay_ms)
        self.house_spawned = False

        self.play_next_music()
        self.adjust_difficulty(0)

    def trigger_screen_shake(self, duration_frames: int = 10, magnitude: int = 6) -> None:
        """触发一次屏幕抖动。

        duration_frames: 抖动持续的帧数
        magnitude: 抖动最大偏移像素
        """
        try:
            # 若已有更长的抖动在进行，不要覆盖为更短的
            if getattr(self, 'screen_shake_timer', 0) < duration_frames:
                self.screen_shake_timer = duration_frames
                self.screen_shake_duration = duration_frames
                self.screen_shake_magnitude = magnitude
            else:
                # 若已有抖动更长，适时提升强度（取较大值）
                self.screen_shake_magnitude = max(getattr(self, 'screen_shake_magnitude', 0), magnitude)
        except Exception:
            pass

    def adjust_difficulty(self, score: int) -> None:
        if not text_target.sprite:
            return
        stage = max(0, score // DIFFICULTY_SCORE_STEP)
        if stage == self.difficulty_stage:
            return
        self.difficulty_stage = stage

        target_speed = min(
            MAX_MOVING_SPEED, MOVING_SPEED + stage * SPEED_INCREMENT
        )
        settings.CURRENT_MOVING_SPEED = target_speed

        def _update_timer(attr_name: str, timer_id: int, base: int, minimum: int, step: int) -> None:
            target_interval = max(minimum, base - step * stage)
            if getattr(self, attr_name) != target_interval:
                setattr(self, attr_name, target_interval)
                pg.time.set_timer(timer_id, int(target_interval))

        _update_timer('tree_spawn_interval', self.tree_timer, TREE_SPAWN_FREQ, TREE_SPAWN_MIN, TREE_SPAWN_STEP)
    # house spawn is managed as a one-time event (HOUSE_FIXED_SPAWN_MS); skip timer updates here
        _update_timer('dog_spawn_interval', self.dog_timer, DOG_SPAWN_FREQ, DOG_SPAWN_MIN, DOG_SPAWN_STEP)

        min_len = min(WORD_LENGTH_CAP, WORD_BASE_MIN_LENGTH + stage)
        max_len = min(WORD_LENGTH_CAP, WORD_BASE_MAX_LENGTH + stage * 2)
        text_target.sprite.set_word_length_range(min_len, max_len)
        

    def draw_penalty_overlay(self) -> None:
        if self.penalty_flash_timer <= 0:
            return
        self.penalty_flash_timer -= 1
        flash_surface = pg.Surface((WIDTH, HEIGHT), pg.SRCALPHA)
        flash_surface.fill((255, 64, 64, 90))
        self.screen.blit(flash_surface, (0, 0))

    def draw_health_bar(self) -> None:
        if getattr(self, 'hud', None):
            return self.hud.draw_health_bar()
        x, y = HEALTH_BAR_POS
        w = HEALTH_BAR_WIDTH
        h = HEALTH_BAR_HEIGHT
        bg_rect = pg.Rect(x, y, w, h)
        pg.draw.rect(self.screen, HEALTH_BAR_BG, bg_rect)
        ratio = max(0, min(1.0, self.health / settings.MAX_HEALTH))
        fg_rect = pg.Rect(x, y, int(w * ratio), h)
        pg.draw.rect(self.screen, HEALTH_BAR_COLOR, fg_rect)
        pg.draw.rect(self.screen, 'black', bg_rect, 3)
        # fallback font when HUD is not present
        try:
            font = pg.font.Font('assets/font/Purrfect.ttf', 28)
        except Exception:
            font = pg.font.SysFont(None, 28)
        text = font.render(f'HP: {self.health}/{settings.MAX_HEALTH}', False, 'white')
        text_rect = text.get_rect(midleft=(x + w + 12, y + h // 2))
        self.screen.blit(text, text_rect)

    def draw_game_over(self) -> None:
        """在屏幕中间显示 GAME OVER 大字与最终分数的覆盖层。"""
        # 半透明暗化背景
        overlay = pg.Surface((WIDTH, HEIGHT), pg.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        # 大字 "GAME OVER"
        go_text = TITLE_FONT.render('GAME OVER', False, 'red')
        go_rect = go_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 80))
        self.screen.blit(go_text, go_rect)

        # 最终得分
        score_text = SCORE_FONT.render(f'Final Score: {self.game_over_score}', False, 'white')
        score_rect = score_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 20))
        self.screen.blit(score_text, score_rect)
        
        # 显示评级
        try:
            rank, color = self.get_rank(self.game_over_score)
            # 创建大号评级字体
            try:
                rank_font = pg.font.Font('assets/font/Purrfect.ttf', 120)
            except Exception:
                rank_font = pg.font.SysFont(None, 120)
            
            rank_text = rank_font.render(rank, True, color)
            rank_rect = rank_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 180))
            
            # 绘制评级背景
            bg_padding = 20
            bg_rect = pg.Rect(
                rank_rect.left - bg_padding,
                rank_rect.top - bg_padding,
                rank_rect.width + bg_padding * 2,
                rank_rect.height + bg_padding * 2
            )
            bg_surface = pg.Surface((bg_rect.width, bg_rect.height), pg.SRCALPHA)
            bg_surface.fill((40, 40, 40, 200))
            pg.draw.rect(bg_surface, color, bg_surface.get_rect(), 4)
            self.screen.blit(bg_surface, bg_rect.topleft)
            
            # 绘制评级字母
            self.screen.blit(rank_text, rank_rect)
            
            # 绘制 "RANK" 标签
            try:
                label_font = pg.font.Font('assets/font/Purrfect.ttf', 24)
            except Exception:
                label_font = pg.font.SysFont(None, 24)
            label_text = label_font.render('RANK', True, (200, 200, 200))
            label_rect = label_text.get_rect(centerx=WIDTH // 2, bottom=rank_rect.top - 5)
            self.screen.blit(label_text, label_rect)
        except Exception:
            pass

    def draw_victory(self) -> None:
        """展示胜利覆盖层（英文）——与 Game Over 类似的样式。"""
        overlay = pg.Surface((WIDTH, HEIGHT), pg.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        self.screen.blit(overlay, (0, 0))

        title = TITLE_FONT.render('YOU MADE IT!', False, 'gold')
        title_rect = title.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 80))
        self.screen.blit(title, title_rect)

        score_text = SCORE_FONT.render(f'Final Score: {self.victory_score}', False, 'white')
        score_rect = score_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 20))
        self.screen.blit(score_text, score_rect)
        
        # 显示评级
        try:
            rank, color = self.get_rank(self.victory_score)
            # 创建大号评级字体
            try:
                rank_font = pg.font.Font('assets/font/Purrfect.ttf', 120)
            except Exception:
                rank_font = pg.font.SysFont(None, 120)
            
            rank_text = rank_font.render(rank, True, color)
            rank_rect = rank_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 180))
            
            # 绘制评级背景
            bg_padding = 20
            bg_rect = pg.Rect(
                rank_rect.left - bg_padding,
                rank_rect.top - bg_padding,
                rank_rect.width + bg_padding * 2,
                rank_rect.height + bg_padding * 2
            )
            bg_surface = pg.Surface((bg_rect.width, bg_rect.height), pg.SRCALPHA)
            bg_surface.fill((40, 40, 40, 200))
            pg.draw.rect(bg_surface, color, bg_surface.get_rect(), 4)
            self.screen.blit(bg_surface, bg_rect.topleft)
            
            # 绘制评级字母
            self.screen.blit(rank_text, rank_rect)
            
            # 绘制 "RANK" 标签
            try:
                label_font = pg.font.Font('assets/font/Purrfect.ttf', 24)
            except Exception:
                label_font = pg.font.SysFont(None, 24)
            label_text = label_font.render('RANK', True, (200, 200, 200))
            label_rect = label_text.get_rect(centerx=WIDTH // 2, bottom=rank_rect.top - 5)
            self.screen.blit(label_text, label_rect)
        except Exception:
            pass

    def draw_level_transition(self) -> None:
        """在两关之间显示过渡提示（如 "LEVEL 2: MINE"）。"""
        overlay = pg.Surface((WIDTH, HEIGHT), pg.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))

        try:
            title = TITLE_FONT.render(self.level_transition_text, False, 'white')
        except Exception:
            try:
                title = pg.font.SysFont(None, 72).render(self.level_transition_text, False, 'white')
            except Exception:
                title = None
        if title:
            rect = title.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            self.screen.blit(title, rect)

    def draw_damage_popups(self) -> None:
        """绘制并更新受伤浮动文字列表。"""
        if getattr(self, 'hud', None):
            return self.hud.draw_damage_popups()
        for popup in self.damage_popups[:]:
            try:
                try:
                    font = pg.font.Font('assets/font/Purrfect.ttf', 24)
                except Exception:
                    font = pg.font.SysFont(None, 24)
                txt = font.render(popup.get('text', '-1 HP'), False, 'salmon')
                txt_rect = txt.get_rect(center=(popup['x'], popup['y']))
                self.screen.blit(txt, txt_rect)
                popup['y'] -= 1
                popup['timer'] -= 1
                if popup['timer'] <= 0:
                    self.damage_popups.remove(popup)
            except Exception:
                try:
                    self.damage_popups.remove(popup)
                except Exception:
                    pass

    def draw_super_jump_notice(self) -> None:
        if getattr(self, 'hud', None):
            return self.hud.draw_super_jump_notice()
        show_notice = ((cat.sprite and cat.sprite.super_jump_ready) or self.super_jump_notice_timer > 0)
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
            try:
                small_font = pg.font.Font('assets/font/Purrfect.ttf', 20)
            except Exception:
                small_font = pg.font.SysFont(None, 20)
            text_surf = small_font.render('SUPER JUMP', False, 'white')
            txt_rect = text_surf.get_rect(center=(badge_w // 2, badge_h // 2))
            badge.blit(text_surf, txt_rect)
            self.screen.blit(badge, (badge_x, badge_y))
        except Exception:
            try:
                small_font = pg.font.SysFont(None, 20)
                notice = small_font.render('SUPER JUMP', False, SUPER_JUMP_TEXT_COLOR)
                notice_rect = notice.get_rect(left=x, top=y + HEALTH_BAR_HEIGHT + 8)
                self.screen.blit(notice, notice_rect)
            except Exception:
                pass
        if self.super_jump_notice_timer > 0:
            self.super_jump_notice_timer -= 1

    def draw_home_screen(self, score: int) -> None:
        self.screen.fill('mediumslateblue')
        if cat.sprite:
            self.screen.blit(cat.sprite.cat_stand, cat.sprite.cat_stand_rect)
        self.screen.blit(self.game_name, self.game_name_rect)
        score_message = SCORE_FONT.render(f'Your score: {score}', False, 'white')
        score_message_rect = score_message.get_rect(center=(WIDTH // 2, SCOREMESSAGE_HEIGHT))
        if score == 0:
            if self.flash_counter % FPS < FPS // 2:
                self.screen.blit(self.game_message, self.game_message_rect)
        else:
            self.screen.blit(score_message, score_message_rect)

    def main_loop(self) -> None:
        while True:
            self.clock.tick(FPS)
            self.flash_counter += 1
            score = text_target.sprite.score if text_target.sprite else 0
            was_active = self.game_active
     
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    exit()
                elif event.type == CORRECT_TYPING and cat.sprite:
                    cat.sprite.start_jump()
                elif event.type == WRONG_TYPING:
                    # 错字触发惩罚（短暂锁定/视觉闪烁）并会造成一次伤害（若未处于无敌）
                    if cat.sprite:
                        cat.sprite.apply_penalty()
                    self.penalty_flash_timer = PENALTY_FLASH_FRAMES
                    # 仅在游戏中且猫当前没有无敌计时器时造成伤害，设置无敌以避免多帧重复扣血
                    if self.game_active and getattr(cat.sprite, 'damage_timer', 0) <= 0:
                        self.health -= 1
                        cat.sprite.damage_timer = settings.DAMAGE_INVULN_FRAMES
                        try:
                            self.lose_sound.play()
                        except Exception:
                            pass
                        # 播放受击音效（错字/惩罚）
                        try:
                            if getattr(self, 'cat_hit_sound', None):
                                self.cat_hit_sound.play()
                        except Exception:
                            pass
                        # 错字导致的伤害也触发抖动
                        try:
                            self.trigger_screen_shake(8, 6)
                        except Exception:
                            pass
                        # 受伤浮动文字
                        try:
                            popup_x = cat.sprite.rect.centerx
                            popup_y = cat.sprite.rect.top - 10
                            self.damage_popups.append({
                                'x': popup_x,
                                'y': popup_y,
                                'timer': settings.DAMAGE_POPUP_FRAMES,
                                'text': '-1 HP'
                            })
                        except Exception:
                            pass
                        # 血量耗尽 -> 触发 Game Over
                        if self.health <= 0:
                            self.game_active = False
                            self.show_game_over = True
                            self.game_over_timer = GAME_OVER_DURATION
                            self.game_over_score = score
                            pg.mixer.music.stop()
                            trees.empty()
                            house.empty()
                            dog.empty()
                elif event.type == SUPER_JUMP_READY and cat.sprite:
                    cat.sprite.enable_super_jump()
                    self.super_jump_notice_timer = SUPER_JUMP_NOTICE_FRAMES
                elif event.type == LAND_EVENT:
                    # 着陆时在地面生成尘土粒子
                    if self.game_active:
                        x = getattr(event, 'x', None)
                        y = getattr(event, 'y', None)
                        if x is None:
                            x = cat.sprite.rect.centerx if cat.sprite else WIDTH // 2
                        if y is None:
                            y = GROUND_HEIGHT
                        self.create_dust(int(x), int(y))
                elif event.type == NEXT_MUSIC and self.game_active:
                    self.play_next_music()

                if self.game_active:
                    if event.type == self.tree_timer:
                        tree_type = choice(list(TREE_TYPE.keys()))
                        # 更平滑的放置策略：基于当前场景中最右侧树的 rightmost + min_gap
                        min_gap = getattr(settings, 'TREE_MIN_GAP', TREE_WIDTH)
                        # 找到当前所有树的最右边（使用 rect.right），若无树则以 WIDTH 为基准
                        try:
                            rightmost = max(t.rect.right for t in trees) if trees else WIDTH
                        except Exception:
                            rightmost = WIDTH
                        # 基于最右边放置下一棵树，附带少量随机偏移以避免过于机械
                        offset = randint(0, max(0, min_gap // 3))
                        spawn_x = max(rightmost + min_gap + offset, WIDTH + offset)
                        trees.add(Trees(tree_type, spawn_x))
                    elif self.item_timer and event.type == self.item_timer:
                        # 控制场上物品数量
                        try:
                            if len(self.items) >= getattr(settings, 'ITEM_MAX_ACTIVE', 2):
                                continue
                        except Exception:
                            pass
                        # 选择物品类型（基于简单权重）
                        try:
                            weights = getattr(settings, 'ITEM_RARITY', {'health':0.6,'shield':0.4})
                            types = [t for t in getattr(settings, 'ITEM_TYPES', ['health','shield'])]
                            total = sum(weights.get(t, 0) for t in types)
                            r = random() * total
                            acc = 0.0
                            chosen = types[0]
                            for t in types:
                                acc += weights.get(t, 0)
                                if r <= acc:
                                    chosen = t
                                    break
                        except Exception:
                            chosen = 'health'
                        # 使用与树类似的 spawn 规则，避免重叠
                        try:
                            min_gap = getattr(settings, 'TREE_MIN_GAP', TREE_WIDTH)
                            rightmost = max(t.rect.right for t in trees) if trees else WIDTH
                            offset = randint(0, max(0, min_gap // 3))
                            spawn_x = max(rightmost + min_gap + offset, WIDTH + offset)
                        except Exception:
                            spawn_x = randint(WIDTH, WIDTH * 2)
                        self.items.add(GroundItem(chosen, spawn_x))
                    elif event.type == self.dog_timer and random() <= EASTEREGG_PROB:
                        dog.add(Dog())
                    elif event.type == pg.KEYDOWN:
                        # 处理滑行按键
                        if event.key == getattr(settings, 'SLIDE_KEY', pg.K_DOWN) and cat.sprite:
                            cat.sprite.start_slide()
                        # 处理打字输入
                        elif text_target.sprite:
                            text_target.sprite.process_key(event.key)
                else:
                    if event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
                        self.reset_run_state()

            text_target.update()

            # 一次性房屋生成：当到达预定时间且尚未生成时生成房屋
            if self.game_active and not getattr(self, 'house_spawned', False):
                spawn_time = getattr(self, 'house_spawn_time_ms', None)
                if spawn_time is not None and pg.time.get_ticks() >= spawn_time:
                    try:
                        house.add(House())
                    except Exception:
                        pass
                    self.house_spawned = True

            # 更新 HUD 动画状态（如平滑血量、徽章淡入淡出）
            if getattr(self, 'hud', None):
                try:
                    self.hud.update()
                except Exception:
                    pass

            if self.game_active:
                trees.update()
                house.update()
                dog.update()
                self.particles.update()
                self.items.update()
                cat.update()
                self.adjust_difficulty(score)
                
                # Boss 系统更新
                if self.boss_active and boss.sprite:
                    boss.update()
                    bullets.update()
                    
                    # Boss 射击逻辑
                    if boss.sprite.should_shoot():
                        bullet_x, bullet_y, bullet_type = boss.sprite.get_bullet_position()
                        bullets.add(Bullet(bullet_x, bullet_y, bullet_type))
                        # 发射子弹时轻微震动
                        try:
                            self.trigger_screen_shake(5, 3)
                        except Exception:
                            pass
                
                # 更新护盾计时器
                if getattr(self, 'shield_active', False) and getattr(self, 'shield_timer', 0) > 0:
                    self.shield_timer -= 1
                    if self.shield_timer <= 0:
                        self.shield_active = False

                # 更新并绘制多层视差背景（天空层先绘制）
                move = settings.CURRENT_MOVING_SPEED
                if getattr(self, 'background', None):
                    try:
                        self.background.update(move)
                        self.background.draw_sky(self.screen)
                        self.background.draw_ground_mid(self.screen)
                    except Exception:
                        # 回退：若 background 出错，尝试旧的字段（若存在）
                        try:
                            for layer in getattr(self, 'sky_layers', []):
                                layer['x'] -= move * layer.get('speed', 0.0)
                                if layer['x'] <= -WIDTH:
                                    layer['x'] += WIDTH
                            for layer in getattr(self, 'ground_layers', []):
                                layer['x'] -= move * layer.get('speed', 0.0)
                                if layer['x'] <= -WIDTH:
                                    layer['x'] += WIDTH
                        except Exception:
                            pass
                        try:
                            for layer in getattr(self, 'sky_layers', []):
                                self.screen.blit(layer['surf'], (int(layer['x']), 0))
                                self.screen.blit(layer['surf'], (int(layer['x']) + WIDTH, 0))
                        except Exception:
                            pass
                        try:
                            if getattr(self, 'ground_layers', None) and len(self.ground_layers) >= 1:
                                mid = self.ground_layers[0]
                                self.screen.blit(mid['surf'], (int(mid['x']), mid['y']))
                                self.screen.blit(mid['surf'], (int(mid['x']) + WIDTH, mid['y']))
                        except Exception:
                            pass

                self.display_score(score)
                # 绘制评级UI
                if getattr(self, 'hud', None):
                    try:
                        self.hud.display_rank(score)
                    except Exception:
                        pass
                # 绘制物品/得分等 HUD 与实体
                # self.display_distance()  # 已移除
                text_target.draw(self.screen)
                trees.draw(self.screen)
                # 绘制道具在树之后/地面之上
                self.items.draw(self.screen)
                # 在树绘制后绘制粒子，让粒子浮于树之上/附近
                self.particles.draw(self.screen)
                house.draw(self.screen)
                dog.draw(self.screen)
                
                # 绘制 Boss 和子弹
                if self.boss_active:
                    bullets.draw(self.screen)
                    boss.draw(self.screen)
                
                cat.draw(self.screen)

                # 绘制前景地面（若存在）——放在角色前方，增加层次感
                if getattr(self, 'background', None):
                    try:
                        self.background.draw_ground_front(self.screen)
                    except Exception:
                        # fallback
                        try:
                            if getattr(self, 'ground_layers', None) and len(self.ground_layers) > 1:
                                front = self.ground_layers[1]
                                self.screen.blit(front['surf'], (int(front['x']), front['y']))
                                self.screen.blit(front['surf'], (int(front['x']) + WIDTH, front['y']))
                        except Exception:
                            pass
                else:
                    if getattr(self, 'ground_layers', None) and len(self.ground_layers) > 1:
                        front = self.ground_layers[1]
                        self.screen.blit(front['surf'], (int(front['x']), front['y']))
                        self.screen.blit(front['surf'], (int(front['x']) + WIDTH, front['y']))

                self.game_active = self.collision()
                self.draw_penalty_overlay()
                self.draw_super_jump_notice()
                # 绘制并更新持续性道具 HUD（如护盾）
                self.draw_active_effects()
                # 绘制生命值条
                self.draw_health_bar()
                # 绘制受伤浮动文字
                self.draw_damage_popups()
                # 绘制滑行按键提示
                if getattr(self, 'hud', None):
                    try:
                        self.hud.draw_slide_hint()
                    except Exception:
                        pass
            else:
                # 如果处于刚刚从运行状态切换过来的情况，播放预游戏音乐
                # 但如果是关卡过渡、胜利或游戏结束状态，不要播放预游戏音乐
                if was_active and not (self.show_level_transition or self.show_victory or self.show_game_over):
                    self.play_pregame_music()
                # 如果处于 Victory 或 Game Over 展示期，绘制对应覆盖并倒计时（优先展示 Victory）
                if self.show_victory:
                    ms_per_frame = int(1000 / FPS)
                    self.victory_timer -= ms_per_frame
                    self.draw_victory()
                    if self.victory_timer <= 0:
                        self.show_victory = False
                        trees.empty()
                        house.empty()
                        dog.empty()
                        try:
                            self.damage_popups.clear()
                        except Exception:
                            pass
                        self.play_pregame_music()
                elif self.show_level_transition:
                    # 在过渡期间显示过渡覆盖并倒计时，过渡结束后恢复游戏
                    # 先绘制新关卡的背景
                    if getattr(self, 'background', None):
                        try:
                            self.background.draw_sky(self.screen)
                            self.background.draw_ground_mid(self.screen)
                        except Exception:
                            self.screen.fill((0, 0, 0))
                    else:
                        self.screen.fill((0, 0, 0))
                    
                    # 然后绘制过渡覆盖层
                    ms_per_frame = int(1000 / FPS)
                    self.level_transition_timer -= ms_per_frame
                    self.draw_level_transition()
                    if self.level_transition_timer <= 0:
                        # 结束过渡，恢复游戏
                        self.show_level_transition = False
                        self.level_transition_timer = 0
                        # 恢复游戏活动状态并播放关卡音乐
                        self.game_active = True
                        try:
                            # 从当前曲目继续播放或启动下一曲
                            self.play_next_music()
                        except Exception:
                            pass
                elif self.show_game_over:
                    # 每帧近似减少的毫秒数（使用固定 FPS 近似，以免改动太多计时逻辑）
                    ms_per_frame = int(1000 / FPS)
                    self.game_over_timer -= ms_per_frame
                    self.draw_game_over()
                    if self.game_over_timer <= 0:
                        # 结束 Game Over 展示，回到预游戏界面
                        self.show_game_over = False
                        trees.empty()
                        house.empty()
                        dog.empty()
                        try:
                            self.damage_popups.clear()
                        except Exception:
                            pass
                        self.play_pregame_music()
                else:
                    self.draw_home_screen(score)

            # 如果处于屏幕抖动状态，将已绘制的画面做随机偏移（帧内平移）
            # 注意：这里对 self.screen 做一次复制并偏移后再刷新屏幕，避免改动大量绘制调用。
            shaking = False
            try:
                if getattr(self, 'screen_shake_timer', 0) > 0:
                    # 先消耗计时器
                    self.screen_shake_timer -= 1
                    # 线性衰减强度
                    dur = max(1, getattr(self, 'screen_shake_duration', 1))
                    decay = self.screen_shake_timer / dur
                    mag = int(getattr(self, 'screen_shake_magnitude', 0) * decay)
                    if mag > 0:
                        shaking = True
                        ox = randint(-mag, mag)
                        oy = randint(-mag, mag)
                        # 复制当前画面并用偏移覆盖
                        tmp = self.screen.copy()
                        # 清空原屏幕（黑色）然后把内容偏移贴回去
                        try:
                            self.screen.fill((0, 0, 0))
                            self.screen.blit(tmp, (ox, oy))
                        except Exception:
                            pass
            except Exception:
                pass

            pg.display.update()

if __name__ == '__main__':
    game = Game()
    game.main_loop()
