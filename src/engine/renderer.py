"""
Enhanced renderer with enemy bullets, muzzle flash, and biome palettes
"""

import math
import os
import random
from typing import List, Tuple
from ..core.player import Player
from ..core.world import World

try:
    import tomllib as toml
except Exception:
    toml = None

WALKABLE = {'.', '·', '~', ' '}

class RaycastingEngine:
    def __init__(self, width: int = 80, height: int = 25, config_path: str = 'config.toml'):
        self.width = width
        self.height = height
        self.fov = math.pi / 3
        self.max_depth = 16.0
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
        self.muzzle_flash_frames = int(g.get('muzzle_flash_frames', 2))
        self.muzzle_flash_brightness = int(g.get('muzzle_flash_brightness', 2))

        self.player = Player(x=1.5, y=1.5, angle=0)
        self.shake_ttl = 0
        self.muzzle_flash_ttl = 0
        self.projectiles = []
        self.banner_cb = None
        self.flash_cb = None
        self.damage_direction_cb = None

    def _apply_shake(self, x: int) -> int:
        if self.camera_shake and self.shake_ttl > 0:
            return max(0, min(self.width - 1, x + random.randint(-self.shake_strength, self.shake_strength)))
        return x

    def damage_feedback(self):
        self.shake_ttl = self.shake_frames
        if self.flash_cb:
            self.flash_cb()

    def muzzle_flash(self):
        self.muzzle_flash_ttl = self.muzzle_flash_frames

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
            if world_map[my][mx] not in WALKABLE:
                return dist, world_map[my][mx]
        return self.max_depth, 'void'

    def correct_fish_eye(self, d: float, a: float) -> float:
        return d * math.cos(a - self.player.angle)

    def _shade(self, distance: float) -> str:
        if distance >= self.max_depth:
            return ' '
        t = distance / self.max_depth
        
        # Muzzle flash brightening effect
        if self.muzzle_flash_ttl > 0 and t < 0.3:  # Brighten center view
            t = max(0, t - self.muzzle_flash_brightness * 0.1)
        
        idx = int(t * (len(self.palette) - 1))
        return self.palette[idx]

    def render_3d(self, world: World, enemies: List = None) -> List[str]:
        if enemies is None:
            enemies = []
        if self.shake_ttl > 0:
            self.shake_ttl -= 1
        if self.muzzle_flash_ttl > 0:
            self.muzzle_flash_ttl -= 1

        screen = [' ' * self.width for _ in range(self.height)]

        # Sky & floor with subtle floor dithering
        for y in range(self.height // 2):
            screen[y] = self.sky_char * self.width
        for y in range(self.height // 2, self.height):
            # Add subtle floor texture variation
            floor_line = ''
            for x in range(self.width):
                if random.random() < 0.05:  # 5% chance for variation
                    floor_line += '·' if self.floor_char == '~' else '~'
                else:
                    floor_line += self.floor_char
            screen[y] = floor_line

        # Walls with enhanced shading
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

        # Render pickups
        for p in getattr(world, 'pickups', []) or []:
            if p.taken:
                continue
            dx = p.x - self.player.x
            dy = p.y - self.player.y
            dist = math.hypot(dx, dy)
            if dist == 0:
                continue
            ang = math.atan2(dy, dx) - self.player.angle
            if abs(ang) < self.fov / 2:
                sx = int((ang + self.fov / 2) / self.fov * self.width)
                sy = self.height // 2
                sx = self._apply_shake(sx)
                if 0 <= sx < self.width:
                    line = screen[sy]
                    sym = p.symbol()[0]
                    screen[sy] = line[:sx] + sym + line[sx+1:]

        # Render enemies
        screen = self.render_enemies(screen, enemies)
        
        # Render enemy projectiles
        screen = self.render_enemy_bullets(screen, enemies)

        # Render player projectiles (rockets)
        for proj in self.projectiles:
            if not proj.get('alive', True):
                continue
            dx = proj['x'] - self.player.x
            dy = proj['y'] - self.player.y
            dist = math.hypot(dx, dy)
            if dist == 0:
                continue
            ang = math.atan2(dy, dx) - self.player.angle
            if abs(ang) < self.fov / 2:
                sx = int((ang + self.fov / 2) / self.fov * self.width)
                sy = self.height // 2
                sx = self._apply_shake(sx)
                if 0 <= sx < self.width:
                    line = screen[sy]
                    screen[sy] = line[:sx] + 'o' + line[sx+1:]

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

    def render_enemy_bullets(self, screen: List[str], enemies: List) -> List[str]:
        """Render enemy projectiles as small dots"""
        for enemy in enemies:
            if not hasattr(enemy, 'projectiles'):
                continue
            for bullet in enemy.projectiles:
                if not bullet.get('alive', True):
                    continue
                dx = bullet['x'] - self.player.x
                dy = bullet['y'] - self.player.y
                dist = math.hypot(dx, dy)
                if dist == 0:
                    continue
                ang = math.atan2(dy, dx) - self.player.angle
                if abs(ang) < self.fov / 2:
                    sx = int((ang + self.fov / 2) / self.fov * self.width)
                    sy = self.height // 2
                    sx = self._apply_shake(sx)
                    if 0 <= sx < self.width:
                        line = screen[sy]
                        screen[sy] = line[:sx] + '*' + line[sx+1:]
        return screen

    def _overlay_weapon(self, screen: List[str]):
        gun = [
            "      __",
            " ___ /__\\____",
            "|___]__________)"
        ]
        
        # Enhance weapon with muzzle flash
        if self.muzzle_flash_ttl > 0:
            gun[2] = gun[2] + " ★"  # Star flash
        
        base_row = self.height - len(gun)
        for i, row in enumerate(gun):
            y = base_row + i
            if 0 <= y < self.height:
                start = max(0, self.width - len(row) - 2)
                line = screen[y]
                row = row[:self.width - start]
                screen[y] = line[:start] + row + line[start+len(row):]

    def move_player(self, key: str):
        speed = float(self.cfg.get('gameplay', {}).get('player_speed', 0.2))
        rot = float(self.cfg.get('gameplay', {}).get('rotate_speed', 0.2))
        if key == 'w':
            dx = speed * math.cos(self.player.angle)
            dy = speed * math.sin(self.player.angle)
            self.player.move(dx, dy)
        elif key == 's':
            dx = -speed * math.cos(self.player.angle)
            dy = -speed * math.sin(self.player.angle)
            self.player.move(dx, dy)
        elif key == 'a':
            self.player.rotate(-rot)
        elif key == 'd':
            self.player.rotate(rot)

    def _hitscan(self, enemies: List, damage: int, aim_tol: float) -> bool:
        safety_radius = float(self.cfg.get('gameplay', {}).get('safety_radius', 0.5))
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
            if abs(diff) < aim_tol and d < min_d:
                min_d = d
                hit_enemy = e
        if hit_enemy and hasattr(hit_enemy, 'take_damage'):
            hit_enemy.take_damage(damage)
            self.player.score += 10
            return True
        return False

    def player_shoot(self, enemies: List = None, mode: str = 'pistol') -> bool:
        if enemies is None:
            enemies = []
        if not self.player.shoot():
            return False
        
        self.muzzle_flash()
        
        gp = self.cfg.get('gameplay', {})
        if mode == 'pistol':
            dmg = int(gp.get('pistol_damage', 25))
            tol = float(gp.get('aim_tolerance', 0.3))
            return self._hitscan(enemies, dmg, tol)
        elif mode == 'shotgun':
            pellets = int(gp.get('shotgun_pellets', 5))
            spread = float(gp.get('shotgun_spread', 0.2))
            dmg = int(gp.get('shotgun_damage', 12))
            tol = float(gp.get('aim_tolerance', 0.3))
            hit = False
            base_angle = self.player.angle
            for i in range(pellets):
                self.player.angle = base_angle + random.uniform(-spread, spread)
                hit = self._hitscan(enemies, dmg, tol) or hit
            self.player.angle = base_angle
            return hit
        elif mode == 'rocket':
            speed = float(gp.get('rocket_speed', 0.6))
            dx = math.cos(self.player.angle) * speed
            dy = math.sin(self.player.angle) * speed
            self.projectiles.append({'x': self.player.x, 'y': self.player.y, 'dx': dx, 'dy': dy, 'alive': True})
            return True
        return False

    def update_projectiles(self, world: World, enemies: List):
        gp = self.cfg.get('gameplay', {})
        radius = float(gp.get('rocket_radius', 1.2))
        damage = int(gp.get('rocket_damage', 40))
        for proj in self.projectiles:
            if not proj.get('alive', True):
                continue
            proj['x'] += proj['dx']
            proj['y'] += proj['dy']
            mx, my = int(proj['x']), int(proj['y'])
            if my < 0 or my >= len(world.map) or mx < 0 or mx >= len(world.map[0]) or world.map[my][mx] not in WALKABLE:
                proj['alive'] = False
                for e in enemies:
                    if getattr(e, 'alive', False):
                        d = math.hypot(e.x - proj['x'], e.y - proj['y'])
                        if d <= radius:
                            e.take_damage(damage)
                if self.banner_cb:
                    self.banner_cb('BOOM!')

    def update_enemy_bullets(self, enemies: List) -> bool:
        """Update enemy bullets and check player hits"""
        player_hit = False
        damage_angle = None
        
        for enemy in enemies:
            if not hasattr(enemy, 'projectiles'):
                continue
            
            for bullet in enemy.projectiles[:]:
                if not bullet.get('alive'):
                    continue
                    
                # Move bullet
                bullet['x'] += bullet['dx']
                bullet['y'] += bullet['dy']
                
                # Check world collision
                if not self._can_move_to(bullet['x'], bullet['y']):
                    bullet['alive'] = False
                    continue
                
                # Check player hit
                if abs(bullet['x'] - self.player.x) < 0.3 and abs(bullet['y'] - self.player.y) < 0.3:
                    bullet['alive'] = False
                    ai_cfg = self.cfg.get('ai', {})
                    damage = int(ai_cfg.get('bullet_damage', 15))
                    self.player.take_damage(damage)
                    
                    # Calculate damage direction
                    damage_angle = math.atan2(bullet['dy'], bullet['dx'])
                    player_hit = True
                    
                    # Trigger feedback
                    self.damage_feedback()
                    if self.damage_direction_cb:
                        self.damage_direction_cb(damage_angle)
        
        return player_hit

    def _can_move_to(self, x: float, y: float) -> bool:
        tx, ty = int(x), int(y)
        # Assume we have world access through game loop
        return True  # Simplified for now

    def try_pickups(self, world: World):
        if not hasattr(world, 'pickups') or not world.pickups:
            return
        for p in world.pickups:
            if p.taken:
                continue
            if abs(p.x - self.player.x) < 0.5 and abs(p.y - self.player.y) < 0.5:
                p.taken = True
                if p.kind == 'health':
                    self.player.heal(p.amount)
                    if self.banner_cb:
                        self.banner_cb('Picked up health')
                elif p.kind == 'ammo':
                    self.player.add_ammo(p.amount)
                    if self.banner_cb:
                        self.banner_cb('Picked up ammo')
                elif p.kind == 'keycard':
                    if self.banner_cb:
                        self.banner_cb('Keycard acquired')

    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')