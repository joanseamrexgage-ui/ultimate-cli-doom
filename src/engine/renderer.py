"""
Depth shading, dithering, and weapon overlay for ASCII renderer
"""

import math
import os
import random
from typing import List, Tuple
from ..core.player import Player
from ..core.world import World

try:
    import tomllib as toml  # py3.11+
except Exception:  # pragma: no cover
    toml = None

class RaycastingEngine:
    def __init__(self, width: int = 80, height: int = 25, config_path: str = 'config.toml'):
        self.width = width
        self.height = height
        self.fov = math.pi / 3
        self.max_depth = 16.0

        # Load config if available
        self.cfg = {}
        if toml is not None:
            try:
                with open(config_path, 'rb') as f:
                    self.cfg = toml.load(f)
            except Exception:
                self.cfg = {}
        
        g = self.cfg.get('graphics', {})
        self.fov = float(g.get('fov', self.fov))
        self.max_depth = float(g.get('max_depth', self.max_depth))
        self.palette = g.get('wall_palette', [' ', '░', '▒', '▓', '█'])
        self.floor_char = g.get('floor_char', '~')
        self.sky_char = g.get('sky_char', '·')
        self.weapon_overlay_enabled = bool(g.get('weapon_overlay', True))
        self.camera_shake = bool(g.get('camera_shake', True))
        self.shake_strength = int(g.get('shake_strength', 1))
        self.shake_frames = int(g.get('shake_frames', 3))

        self.player = Player(x=1.5, y=1.5, angle=0)
        self.shake_ttl = 0

    def _apply_shake(self, x: int) -> int:
        if self.camera_shake and self.shake_ttl > 0:
            return max(0, min(self.width - 1, x + random.randint(-self.shake_strength, self.shake_strength)))
        return x

    def damage_feedback(self):
        self.shake_ttl = self.shake_frames

    def cast_ray(self, angle: float, world_map: List[str]) -> Tuple[float, str]:
        ox = self.player.x
        oy = self.player.y
        dx = math.cos(angle)
        dy = math.sin(angle)

        step = 0.02
        dist = 0.0
        while dist < self.max_depth:
            ox += dx * step
            oy += dy * step
            dist += step
            mx, my = int(ox), int(oy)
            if my < 0 or my >= len(world_map) or mx < 0 or mx >= len(world_map[0]):
                return self.max_depth, 'void'
            if world_map[my][mx] not in ['.', '·', '~', ' ']:
                return dist, world_map[my][mx]
        return self.max_depth, 'void'

    def correct_fish_eye(self, d: float, a: float) -> float:
        return d * math.cos(a - self.player.angle)

    def _shade(self, distance: float) -> str:
        # Map distance to palette index with simple dithering
        if distance >= self.max_depth:
            return ' '
        t = distance / self.max_depth
        idx = int(t * (len(self.palette) - 1))
        return self.palette[idx]

    def render_3d(self, world: World, enemies: List = None) -> List[str]:
        if enemies is None:
            enemies = []
        if self.shake_ttl > 0:
            self.shake_ttl -= 1

        screen = [' ' * self.width for _ in range(self.height)]

        # sky & floor
        for y in range(self.height // 2):
            screen[y] = self.sky_char * self.width
        for y in range(self.height // 2, self.height):
            screen[y] = self.floor_char * self.width

        for col in range(self.width):
            sc = self._apply_shake(col)
            ray_angle = (self.player.angle - self.fov / 2 + col / self.width * self.fov)
            distance, wall_type = self.cast_ray(ray_angle, world.map)
            cd = self.correct_fish_eye(distance, ray_angle)
            wall_height = self.height if cd <= 0.1 else min(self.height, int(self.height / cd))
            ch = self._shade(cd)
            y0 = max(0, self.height // 2 - wall_height // 2)
            y1 = min(self.height, self.height // 2 + wall_height // 2)
            for row in range(y0, y1):
                line = screen[row]
                screen[row] = line[:sc] + ch + line[sc+1:]

        screen = self.render_enemies(screen, enemies)
        if self.weapon_overlay_enabled:
            self._overlay_weapon(screen)
        return screen

    def render_enemies(self, screen: List[str], enemies: List) -> List[str]:
        for enemy in enemies:
            if not getattr(enemy, 'alive', False):
                continue
            dx = enemy.x - self.player.x
            dy = enemy.y - self.player.y
            dist = math.hypot(dx, dy)
            if dist == 0:
                continue
            ang = math.atan2(dy, dx) - self.player.angle
            if abs(ang) < self.fov / 2:
                sx = int((ang + self.fov / 2) / self.fov * self.width)
                sy = self.height // 2
                sx = self._apply_shake(sx)
                if 0 <= sx < self.width:
                    sprite = enemy.get_sprite(dist) if hasattr(enemy, 'get_sprite') else '👾'
                    line = screen[sy]
                    screen[sy] = line[:sx] + sprite[0] + line[sx+1:]
        return screen

    def _overlay_weapon(self, screen: List[str]):
        gun = [
            "      __",
            " ___ /__\\____",
            "|___]__________)"
        ]
        base_row = self.height - len(gun)
        for i, row in enumerate(gun):
            y = base_row + i
            if 0 <= y < self.height:
                start = max(0, self.width - len(row) - 2)
                line = screen[y]
                row = row[:self.width - start]
                screen[y] = line[:start] + row + line[start+len(row):]

    def move_player(self, key: str):
        speed = 0.2
        if key == 'w':
            dx = speed * math.cos(self.player.angle)
            dy = speed * math.sin(self.player.angle)
            self.player.move(dx, dy)
        elif key == 's':
            dx = -speed * math.cos(self.player.angle)
            dy = -speed * math.sin(self.player.angle)
            self.player.move(dx, dy)
        elif key == 'a':
            self.player.rotate(-0.2)
        elif key == 'd':
            self.player.rotate(0.2)

    def player_shoot(self, enemies: List = None) -> bool:
        if enemies is None:
            enemies = []
        if not self.player.shoot():
            return False
        safety_radius = float(self.cfg.get('gameplay', {}).get('safety_radius', 0.5))
        aim_tolerance = float(self.cfg.get('gameplay', {}).get('aim_tolerance', 0.3))
        hit_enemy = None
        min_d = float('inf')
        for e in enemies:
            if not getattr(e, 'alive', False):
                continue
            dx = e.x - self.player.x
            dy = e.y - self.player.y
            d = math.hypot(dx, dy)
            if d < safety_radius:
                continue
            ang = math.atan2(dy, dx)
            diff = (ang - self.player.angle + math.pi) % (2*math.pi) - math.pi
            if abs(diff) < aim_tolerance and d < min_d:
                min_d = d
                hit_enemy = e
        if hit_enemy and hasattr(hit_enemy, 'take_damage'):
            hit_enemy.take_damage(int(self.cfg.get('gameplay', {}).get('pistol_damage', 25)))
            self.player.score += 10
            return True
        return False

    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')
