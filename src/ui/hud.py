"""
ASCII HUD overlay for Ultimate CLI DOOM
Displays health, ammo, score, level and mini status bar
"""

from typing import List, Dict

class GameHUD:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height

    def _bar(self, label: str, value: int, max_value: int, width: int = 20, fill_char: str = '█') -> str:
        value = max(0, min(value, max_value))
        filled = int(width * (value / max_value)) if max_value > 0 else 0
        empty = width - filled
        return f"{label}:[{fill_char*filled}{' ' * empty}] {value}/{max_value}"

    def add_overlay(self, frame: List[str], stats: Dict[str, int]) -> List[str]:
        """Overlay HUD on top of existing frame"""
        hud_lines = []
        hud_lines.append(f"LEVEL {stats.get('level', 1):>2}  SCORE: {stats.get('score', 0):>6}")
        hud_lines.append(self._bar('HP ', stats.get('health', 100), 100, width=24))
        hud_lines.append(self._bar('AMM', stats.get('ammo', 0), 100, width=24, fill_char='▓'))

        # Place HUD at top 3 lines
        new_frame = frame[:]
        for i, hud in enumerate(hud_lines):
            line = (hud + ' ' * self.width)[:self.width]
            new_frame[i] = line
        return new_frame
