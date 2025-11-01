"""
HUD feedback: damage flash, pickup notifications
"""

from typing import List, Dict

class GameHUD:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.flash_ttl = 0
        self.flash_char = '#'
        self.flash_rows = 1
        self.banner = ''
        self.banner_ttl = 0

    def damage_flash(self, frames: int = 2):
        self.flash_ttl = frames

    def notify(self, text: str, frames: int = 30):
        self.banner = text
        self.banner_ttl = frames

    def _bar(self, label: str, value: int, max_value: int, width: int = 20, fill_char: str = '█') -> str:
        value = max(0, min(value, max_value))
        filled = int(width * (value / max_value)) if max_value > 0 else 0
        empty = width - filled
        return f"{label}:[{fill_char*filled}{' ' * empty}] {value}/{max_value}"

    def add_overlay(self, frame: List[str], stats: Dict[str, int]) -> List[str]:
        hud_lines = []
        hud_lines.append(f"LEVEL {stats.get('level', 1):>2}  SCORE: {stats.get('score', 0):>6}")
        hud_lines.append(self._bar('HP ', stats.get('health', 100), 100, width=24))
        hud_lines.append(self._bar('AMM', stats.get('ammo', 0), 100, width=24, fill_char='▓'))

        new_frame = frame[:]
        for i, hud in enumerate(hud_lines):
            line = (hud + ' ' * self.width)[:self.width]
            new_frame[i] = line

        # damage flash
        if self.flash_ttl > 0:
            self.flash_ttl -= 1
            mask = self.flash_char * self.width
            for i in range(self.flash_rows):
                new_frame[i] = mask

        # banner notifications
        if self.banner_ttl > 0 and self.banner:
            self.banner_ttl -= 1
            text = f"*** {self.banner} ***"
            start = max(0, (self.width - len(text)) // 2)
            y = len(hud_lines)
            line = new_frame[y]
            text = text[:self.width - start]
            new_frame[y] = line[:start] + text + line[start+len(text):]

        return new_frame
