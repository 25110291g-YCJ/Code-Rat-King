from random import choice

import pygame as pg
from settings import *


class TextTarget(pg.sprite.Sprite):
    """打字目标精灵，负责显示单词、计算得分与连击奖励。"""

    def __init__(self) -> None:
        super().__init__()
        self.letter_count = 0
        self.score = 0
        self.word_length_range = (WORD_BASE_MIN_LENGTH, WORD_BASE_MAX_LENGTH)
        self.feedback_color = TARGET_TEXT_COLOR
        self.feedback_timer = 0
        self.combo_count = 0
        
        # New state variables for better rendering
        self.full_text = ''
        self.typed_index = 0
        
        self.hit_sound = pg.mixer.Sound(HIT_SOUND)

        # Initialize fonts once
        self.font = TARGET_FONT
        
        # Dirty flag to control rendering
        self.dirty = False

        self.pick_new_word()

    def _cache_static_surfaces(self) -> None:
        """Cache static surfaces that don't change during typing."""
        # Cache English shadow (full word)
        self.cached_en_shadow = self.font.render(self.full_text, False, (0, 0, 0))

    def update_text(self) -> None:
        # Render parts
        typed_part = self.full_text[:self.typed_index]
        untyped_part = self.full_text[self.typed_index:]
        
        # Colors
        typed_color = (255, 215, 0) # Gold for typed part
        untyped_color = self.feedback_color
        
        # Render surfaces
        typed_surf = self.font.render(typed_part, False, typed_color)
        untyped_surf = self.font.render(untyped_part, False, untyped_color)
        
        # Calculate total width for English text
        en_width = typed_surf.get_width() + untyped_surf.get_width()
        en_height = max(typed_surf.get_height(), untyped_surf.get_height())
        
        total_width = en_width + 20
        total_height = en_height + 10
            
        # Create main surface
        self.image = pg.Surface((total_width, total_height), pg.SRCALPHA)
        
        # Center English text horizontally
        en_x = (total_width - en_width) // 2
        
        # Draw Shadow for English text (offset 4, 4)
        if hasattr(self, 'cached_en_shadow'):
            self.image.blit(self.cached_en_shadow, (en_x + 4, 4))
        else:
            # Fallback if not cached yet
            shadow = self.font.render(self.full_text, False, (0, 0, 0))
            self.image.blit(shadow, (en_x + 4, 4))
        
        # Draw Typed and Untyped
        self.image.blit(typed_surf, (en_x, 0))
        self.image.blit(untyped_surf, (en_x + typed_surf.get_width(), 0))
            
        self.rect = self.image.get_rect(center=(WIDTH // 2, TEXTTARGET_HEIGHT))

    def pick_new_word(self) -> None:
        min_len, max_len = self.word_length_range
        
        # Filter candidates
        valid_candidates = []
        for item in WORDBANK:
            if isinstance(item, dict):
                word = item['en']
            else:
                word = item
            
            if min_len <= len(word) <= max_len:
                valid_candidates.append(item)
        
        if not valid_candidates:
            valid_candidates = WORDBANK

        choice_item = choice(valid_candidates)
        
        if isinstance(choice_item, dict):
            self.full_text = choice_item['en']
        else:
            self.full_text = choice_item
            
        self.typed_index = 0
        self.candidate = self.full_text # Keep for compatibility if needed, but logic uses full_text
        
        # Pre-render static parts
        self._cache_static_surfaces()
        self.update_text()

    def set_word_length_range(self, min_len: int, max_len: int) -> None:
        min_len = max(1, min_len)
        max_len = max(min_len, max_len)
        self.word_length_range = (
            min(min_len, WORD_LENGTH_CAP), min(max_len, WORD_LENGTH_CAP)
        )

    def process_event(self, event: pg.event.Event) -> None:
        """Process a keyboard event directly."""
        if not self.full_text:
            return
            
        # Use event.unicode if available (most reliable for typing)
        char = getattr(event, 'unicode', '')
        
        # If unicode is empty (e.g. special keys), fallback to key name
        if not char:
            try:
                char = pg.key.name(event.key)
            except:
                return
        
        # Filter: must be a single character and must be a letter (or space if needed)
        if len(char) != 1:
            return
            
        if not char.isalpha():
            return
            
        pressed = char.lower()
        
        # Check if we are done
        if self.typed_index >= len(self.full_text):
            return

        target = self.full_text[self.typed_index].lower()
        if pressed == target:
            self._handle_correct_letter()
        else:
            self._handle_miss()

    def process_key(self, key: int) -> None:
        # Deprecated, use process_event instead
        pass

    def _handle_correct_letter(self) -> None:
        self.typed_index += 1
        self.letter_count += 1
        # 增加连击计数并根据连击倍率计算分数
        self.combo_count += 1
        try:
            multiplier = self.combo_multiplier()
        except Exception:
            multiplier = 1.0
        # 使用 letter_count 与倍率的组合来计算当前分数（整型显示）
        self.score = int(self.letter_count * multiplier)
        self.feedback_color = TARGET_TEXT_COLOR
        self.feedback_timer = 0
        self.hit_sound.play()
        self.dirty = True
        
        # Check completion
        if self.typed_index >= len(self.full_text):
            pg.event.post(pg.event.Event(CORRECT_TYPING))
            self.pick_new_word()
        self._check_combo_reward()

    def _handle_miss(self) -> None:
        self.combo_count = 0
        self.feedback_color = TARGET_ALERT_COLOR
        self.feedback_timer = MISS_FEEDBACK_FRAMES
        self.dirty = True
        pg.event.post(pg.event.Event(WRONG_TYPING))

    def _check_combo_reward(self) -> None:
        if self.combo_count >= COMBO_THRESHOLD:
            self.combo_count = 0
            self.letter_count += SUPER_JUMP_BONUS
            try:
                self.score = int(self.letter_count * self.combo_multiplier())
            except Exception:
                self.score = self.letter_count
            pg.event.post(pg.event.Event(SUPER_JUMP_READY))

    def combo_multiplier(self) -> float:
        """基于当前连击返回分数倍率。

        每 COMBO_STEP 个连击增加 COMBO_BONUS 的倍率，最高为 COMBO_MAX_MULTIPLIER。
        """
        try:
            steps = max(0, self.combo_count // COMBO_STEP)
            bonus = steps * COMBO_BONUS
            mult = 1.0 + bonus
            return min(mult, COMBO_MAX_MULTIPLIER)
        except Exception:
            return 1.0

    def update(self) -> None:
        if self.feedback_timer > 0:
            self.feedback_timer -= 1
            if self.feedback_timer == 0:
                self.feedback_color = TARGET_TEXT_COLOR
                self.dirty = True
        
        if self.dirty:
            self.update_text()
            self.dirty = False
