from random import choice

import pygame as pg
from settings import *
import settings


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
        self.candidate = ''
        self.hit_sound = pg.mixer.Sound(HIT_SOUND)
        self.pick_new_word()

    def update_text(self) -> None:
        self.image = TARGET_FONT.render(self.candidate, False, self.feedback_color)
        self.rect = self.image.get_rect(center=(WIDTH // 2, TEXTTARGET_HEIGHT))

    def pick_new_word(self) -> None:
        min_len, max_len = self.word_length_range
        candidates = [word for word in WORDBANK if min_len <= len(word) <= max_len]
        if not candidates:
            candidates = WORDBANK
        self.candidate = choice(candidates)
        self.update_text()

    def set_word_length_range(self, min_len: int, max_len: int) -> None:
        min_len = max(1, min_len)
        max_len = max(min_len, max_len)
        self.word_length_range = (
            min(min_len, WORD_LENGTH_CAP), min(max_len, WORD_LENGTH_CAP)
        )

    def process_key(self, key: int) -> None:
        if not self.candidate:
            return
        key_name = pg.key.name(key)
        if len(key_name) != 1 or not key_name.isalpha():
            return
        pressed = key_name.lower()
        target = self.candidate[0]
        if pressed == target:
            self._handle_correct_letter()
        else:
            self._handle_miss()

    def _handle_correct_letter(self) -> None:
        self.candidate = self.candidate[1:]
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
        self.update_text()
        if not self.candidate:
            pg.event.post(pg.event.Event(CORRECT_TYPING))
            self.pick_new_word()
        self._check_combo_reward()

    def _handle_miss(self) -> None:
        self.combo_count = 0
        self.feedback_color = TARGET_ALERT_COLOR
        self.feedback_timer = MISS_FEEDBACK_FRAMES
        self.update_text()
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
                self.update_text()
