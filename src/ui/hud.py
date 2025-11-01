"""
📊 Enhanced HUD with compass, damage direction, and muzzle flash feedback
"""

from typing import List, Dict
import math

class GameHUD:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.flash_ttl = 0
        self.flash_char = '#'
        self.flash_rows = 1
        self.banner = ''
        self.banner_ttl = 0
        
        # Damage direction indicator
        self.damage_direction = None
        self.damage_direction_ttl = 0
        
        # Muzzle flash effect
        self.muzzle_flash_ttl = 0
        
        # Compass and objective tracking
        self.objective_angle = None
        self.objective_text = "EXPLORE"

    def damage_flash(self, frames: int = 3):
        self.flash_ttl = frames

    def set_damage_direction(self, angle: float, frames: int = 15):
        """Set damage direction indicator (angle in radians)"""
        self.damage_direction = angle
        self.damage_direction_ttl = frames

    def muzzle_flash(self, frames: int = 2):
        """Trigger muzzle flash effect"""
        self.muzzle_flash_ttl = frames

    def set_objective(self, angle: float = None, text: str = "EXPLORE"):
        """Set objective direction and text"""
        self.objective_angle = angle
        self.objective_text = text

    def notify(self, text: str, frames: int = 30):
        self.banner = text
        self.banner_ttl = frames

    def _bar(self, label: str, value: int, max_value: int, width: int = 20, fill_char: str = '█') -> str:
        value = max(0, min(value, max_value))
        filled = int(width * (value / max_value)) if max_value > 0 else 0
        empty = width - filled
        return f"{label}:[{fill_char*filled}{' ' * empty}] {value}/{max_value}"

    def _get_compass_line(self, player_angle: float) -> str:
        """Generate compass with N/E/S/W markers and objective indicator"""
        # Normalize angle to 0-2π
        angle = (player_angle + 2 * math.pi) % (2 * math.pi)
        
        # Convert to compass bearing (0 = North)
        bearing = (angle - math.pi/2 + 2 * math.pi) % (2 * math.pi)
        
        # Create base compass
        compass_width = min(16, self.width - 20)
        compass = [' '] * compass_width
        
        # Mark cardinal directions
        north_pos = int((0 - bearing) / (2 * math.pi) * compass_width) % compass_width
        east_pos = int((math.pi/2 - bearing) / (2 * math.pi) * compass_width) % compass_width
        south_pos = int((math.pi - bearing) / (2 * math.pi) * compass_width) % compass_width
        west_pos = int((3*math.pi/2 - bearing) / (2 * math.pi) * compass_width) % compass_width
        
        compass[north_pos] = 'N'
        compass[east_pos] = 'E'
        compass[south_pos] = 'S'
        compass[west_pos] = 'W'
        
        # Mark objective if set
        if self.objective_angle is not None:
            obj_pos = int((self.objective_angle - bearing) / (2 * math.pi) * compass_width) % compass_width
            compass[obj_pos] = '▶'  # Objective marker
        
        return f"[{''.join(compass)}] {self.objective_text}"

    def _get_damage_indicator(self) -> str:
        """Get damage direction arrow"""
        if self.damage_direction_ttl <= 0:
            return ""
        
        # Convert angle to arrow
        angle = self.damage_direction
        if angle is None:
            return ""
            
        # Normalize to 0-2π
        angle = (angle + 2 * math.pi) % (2 * math.pi)
        
        if angle < math.pi/4 or angle >= 7*math.pi/4:
            arrow = "→"  # Right
        elif angle < 3*math.pi/4:
            arrow = "↓"  # Down
        elif angle < 5*math.pi/4:
            arrow = "←"  # Left
        else:
            arrow = "↑"  # Up
            
        return f"DMG {arrow}"

    def add_overlay(self, frame: List[str], stats: Dict[str, int], player_angle: float = 0) -> List[str]:
        """Enhanced overlay with compass and damage indicators"""
        # Update timers
        if self.damage_direction_ttl > 0:
            self.damage_direction_ttl -= 1
        if self.muzzle_flash_ttl > 0:
            self.muzzle_flash_ttl -= 1
            
        hud_lines = []
        
        # Top line: Compass and damage indicator
        compass_line = self._get_compass_line(player_angle)
        damage_indicator = self._get_damage_indicator()
        top_line = f"{compass_line[:35]} {damage_indicator}"
        hud_lines.append((top_line + ' ' * self.width)[:self.width])
        
        # Stats lines
        hud_lines.append(f"LEVEL {stats.get('level', 1):>2}  SCORE: {stats.get('score', 0):>6}")
        hud_lines.append(self._bar('HP ', stats.get('health', 100), 100, width=24))
        hud_lines.append(self._bar('AMM', stats.get('ammo', 0), 100, width=24, fill_char='▓'))

        new_frame = frame[:]
        for i, hud in enumerate(hud_lines):
            if i < len(new_frame):
                line = (hud + ' ' * self.width)[:self.width]
                new_frame[i] = line

        # Damage flash effect
        if self.flash_ttl > 0:
            self.flash_ttl -= 1
            mask = self.flash_char * self.width
            for i in range(min(self.flash_rows, len(new_frame))):
                new_frame[i] = mask

        # Banner notifications
        if self.banner_ttl > 0 and self.banner:
            self.banner_ttl -= 1
            text = f"*** {self.banner} ***"
            start = max(0, (self.width - len(text)) // 2)
            y = min(len(hud_lines), len(new_frame) - 1)
            if y >= 0:
                line = new_frame[y]
                text = text[:self.width - start]
                new_frame[y] = line[:start] + text + line[start+len(text):]

        return new_frame