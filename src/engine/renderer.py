"""
ULTIMATE NEXT-GEN CLI Graphics Renderer
Revolutionary ASCII ray-tracing with volumetrics, reflections, and post-processing
"""

import math
import os
import random
from typing import List, Tuple
from ..core.player import Player
from ..core.world import World
from .graphics_fx import NextGenGraphicsFX

try:
    import tomllib as toml
except Exception:
    toml = None

WALKABLE = {'.', '·', '~', ' '}

# Enhanced wall material mappings with shader properties
WALL_MATERIALS = {
    'stone': {
        'symbols': ['▒', '▓', '█'], 
        'base': '▒',
        'reflectivity': 0.1,
        'roughness': 0.8,
        'parallax_scale': 0.3
    },
    'brick': {
        'symbols': ['░', '▒', '▓'], 
        'base': '░',
        'reflectivity': 0.05,
        'roughness': 0.9,
        'parallax_scale': 0.4
    },  
    'metal': {
        'symbols': ['█', '▓', '▒'], 
        'base': '█',
        'reflectivity': 0.7,
        'roughness': 0.2,
        'parallax_scale': 0.1
    },
    'wood': {
        'symbols': ['║', '│', '┃'], 
        'base': '║',
        'reflectivity': 0.0,
        'roughness': 0.7,
        'parallax_scale': 0.5
    }
}

class UltimateRaycastingEngine:
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
        
        # Navigation aids
        self.minimap_enabled = bool(g.get('minimap_enabled', True))
        self.minimap_width = int(g.get('minimap_width', 15))
        self.minimap_height = int(g.get('minimap_height', 8))
        self.materials_enabled = bool(g.get('materials_enabled', True))
        
        # Initialize ULTIMATE graphics FX system
        self.gfx = NextGenGraphicsFX(self.cfg)
        
        # Enhanced tracking systems
        self.visited = set()
        self.frame_buffer = []  # For motion blur
        self.player_velocity = 0.0
        self.last_player_pos = (0.0, 0.0)

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

    def _get_wall_material_char_next_gen(self, wall_type: str, distance: float, world: World, hit_x: int, hit_y: int, angle: float) -> str:
        """Next-gen wall rendering with shaders, lighting, and materials"""
        if not self.materials_enabled:
            return self._shade(distance)
            
        # Get material properties
        material = getattr(world, 'material', 'stone')
        if hasattr(world, 'theme'):
            material_map = {
                'quantum': 'metal',
                'atman': 'stone', 
                'loqiemean': 'brick',
                'batut': 'wood'
            }
            material = material_map.get(world.theme, 'stone')
        
        if distance >= self.max_depth:
            return ' '
            
        mat_data = WALL_MATERIALS.get(material, WALL_MATERIALS['stone'])
        symbols = mat_data['symbols']
        
        # Base distance shading
        t = min(0.99, distance / self.max_depth)
        
        # NEXT-GEN SHADER PIPELINE:
        
        # 1. Parallax mapping
        parallax_offset = 0
        if abs(angle) < math.pi/4:  # Front-facing walls
            parallax_scale = mat_data['parallax_scale']
            view_angle = abs(angle)
            parallax_offset = int(view_angle * parallax_scale * 2)
        
        # 2. Enhanced lighting with GI
        light_intensity = self.gfx.get_enhanced_light_intensity(hit_x, hit_y, world.map if hasattr(world, 'map') else None)
        
        # 3. Wall damage effects
        if self.gfx.destructibles:
            base_char = self.gfx.get_damaged_wall_char(hit_x, hit_y, symbols[0])
        else:
            base_char = symbols[0]
        
        # 4. Apply all effects
        t = max(0, t / light_intensity)  # Lighting brightens
        
        # Muzzle flash brightening
        if self.muzzle_flash_ttl > 0 and t < 0.3:
            t = max(0, t - self.muzzle_flash_brightness * 0.1)
        
        # 5. Final character selection with parallax
        idx = max(0, min(len(symbols) - 1, int(t * (len(symbols) - 1)) + parallax_offset))
        final_char = symbols[idx]
        
        # 6. Reflections for metal surfaces
        if material == 'metal' and self.gfx.reflections and random.random() < mat_data['reflectivity']:
            reflection = self.gfx.calculate_reflection(0, 0, world.map, self.player.x, self.player.y, self.player.angle)
            if reflection != ' ':
                final_char = reflection
        
        return final_char

    def cast_ray_next_gen(self, angle: float, world_map: List[str]) -> Tuple[float, str, int, int, float]:
        """Enhanced ray casting with material properties"""
        ox = self.player.x
        oy = self.player.y
        dx = math.cos(angle)
        dy = math.sin(angle)
        step = 0.015  # Higher precision for better effects
        dist = 0.0
        hit_x, hit_y = 0, 0
        surface_normal = 0.0
        
        while dist < self.max_depth:
            ox += dx * step
            oy += dy * step
            dist += step
            mx, my = int(ox), int(oy)
            
            # Enhanced visited tracking
            if 0 <= mx < 100 and 0 <= my < 100:
                self.visited.add((mx, my))
            
            if my < 0 or my >= len(world_map) or mx < 0 or mx >= len(world_map[0]):
                return self.max_depth, 'void', mx, my, 0.0
            
            if world_map[my][mx] not in WALKABLE:
                # Calculate surface normal for shader effects
                surface_normal = math.atan2(my - self.player.y, mx - self.player.x)
                return dist, world_map[my][mx], mx, my, surface_normal
            
            hit_x, hit_y = mx, my
            
        return self.max_depth, 'void', hit_x, hit_y, surface_normal

    def correct_fish_eye(self, d: float, a: float) -> float:
        return d * math.cos(a - self.player.angle)

    def _shade(self, distance: float) -> str:
        """Fallback shading"""
        if distance >= self.max_depth:
            return ' '
        t = distance / self.max_depth
        
        if self.muzzle_flash_ttl > 0 and t < 0.3:
            t = max(0, t - self.muzzle_flash_brightness * 0.1)
        
        idx = int(t * (len(self.palette) - 1))
        return self.palette[idx]

    def _render_minimap(self, screen: List[str], world: World, enemies: List) -> List[str]:
        """Enhanced minimap with better visualization"""
        if not self.minimap_enabled:
            return screen
            
        px, py = int(self.player.x), int(self.player.y)
        map_h, map_w = len(world.map), len(world.map[0])
        
        start_x = max(0, px - self.minimap_width // 2)
        start_y = max(0, py - self.minimap_height // 2)
        end_x = min(map_w, start_x + self.minimap_width)
        end_y = min(map_h, start_y + self.minimap_height)
        
        minimap_screen_x = self.width - self.minimap_width - 1
        minimap_screen_y = 4
        
        for my in range(start_y, end_y):
            screen_y = minimap_screen_y + (my - start_y)
            if screen_y >= len(screen):
                break
                
            line = screen[screen_y]
            
            for mx in range(start_x, end_x):
                screen_x = minimap_screen_x + (mx - start_x)
                if screen_x >= self.width:
                    break
                    
                if (mx, my) not in self.visited:
                    continue
                    
                char = '?'
                
                # Enhanced minimap symbols
                if abs(mx - px) < 1 and abs(my - py) < 1:
                    char = '◎'  # Enhanced player symbol
                elif any(abs(e.x - mx - 0.5) < 1 and abs(e.y - my - 0.5) < 1 
                        and getattr(e, 'alive', False) for e in enemies):
                    char = '⚠'  # Warning for enemies
                elif hasattr(world, 'doors'):
                    door = next((d for d in world.doors if d.x == mx and d.y == my), None)
                    if door:
                        char = '■' if door.locked else '□'
                elif hasattr(world, 'exits'):
                    exit_obj = next((e for e in world.exits if e.x == mx and e.y == my), None)
                    if exit_obj:
                        char = '▶' if exit_obj.active else '▷'
                elif hasattr(world, 'pickups'):
                    pickup = next((p for p in world.pickups 
                                 if not p.taken and abs(p.x - mx - 0.5) < 1 and abs(p.y - my - 0.5) < 1), None)
                    if pickup:
                        char = '♥' if pickup.kind == 'health' else ('◈' if pickup.kind == 'ammo' else '★')
                # Fluids on minimap
                elif (mx, my) in self.gfx.fluids:
                    char = '●'
                elif world.map[my][mx] not in WALKABLE:
                    char = '■'
                else:
                    char = '·'
                
                screen[screen_y] = line[:screen_x] + char + line[screen_x + 1:]
        
        return screen

    def render_3d_next_gen(self, world: World, enemies: List = None) -> List[str]:
        """ULTIMATE next-gen 3D rendering pipeline"""
        if enemies is None:
            enemies = []
        
        # Update player velocity for motion blur
        current_pos = (self.player.x, self.player.y)
        self.player_velocity = math.hypot(
            current_pos[0] - self.last_player_pos[0],
            current_pos[1] - self.last_player_pos[1]
        )
        self.last_player_pos = current_pos
        
        if self.shake_ttl > 0:
            self.shake_ttl -= 1
        if self.muzzle_flash_ttl > 0:
            self.muzzle_flash_ttl -= 1

        # Update next-gen graphics systems
        self.gfx.update()
        self.gfx.update_light_sources(world.map)

        screen = [' ' * self.width for _ in range(self.height)]
        sky_height = self.height // 2
        
        # RENDER PIPELINE:
        
        # 1. Enhanced animated sky with multiple layers
        theme = getattr(world, 'theme', 'quantum')
        screen = self.gfx.render_enhanced_sky(screen, self.width, sky_height, theme)
        
        # 2. Volumetric lighting rays
        screen = self.gfx.render_volumetric_lighting(screen, self.width, self.height, world.map)

        # 3. Enhanced floor with fluid layer
        for y in range(self.height // 2, self.height):
            floor_line = ''
            floor_chars = [self.floor_char]
            if hasattr(world, 'theme'):
                theme_floors = {
                    'quantum': ['.', '·', '¨', '⋅'],
                    'atman': ['·', '∘', '°', '◦'],
                    'loqiemean': ['~', '≈', '∼', '〜'],
                    'batut': [' ', '·', '`', '‵']
                }
                floor_chars = theme_floors.get(world.theme, [self.floor_char])
            
            for x in range(self.width):
                # Enhanced floor variation with SSAO
                ssao_factor = self.gfx.calculate_ssao(screen, x, y)
                variation_chance = 0.12 * ssao_factor
                
                if random.random() < variation_chance:
                    floor_line += random.choice(floor_chars)
                else:
                    floor_line += floor_chars[0]
            screen[y] = floor_line
        
        # Apply fluid layer to floor
        screen = self.gfx.render_fluid_layer(screen, world.map)

        # 4. NEXT-GEN WALL RENDERING with full shader pipeline
        for col in range(self.width):
            sc = self._apply_shake(col)
            ray_angle = (self.player.angle - self.fov / 2 + col / self.width * self.fov)
            distance, wall_type, hit_x, hit_y, surface_normal = self.cast_ray_next_gen(ray_angle, world.map)
            cd = self.correct_fish_eye(distance, ray_angle)
            wall_height = self.height if cd <= 0.1 else min(self.height, int(self.height / cd))
            
            # Next-gen material character with full effects
            ch = self._get_wall_material_char_next_gen(wall_type, cd, world, hit_x, hit_y, surface_normal)
            
            y0 = max(0, self.height // 2 - wall_height // 2)
            y1 = min(self.height, self.height // 2 + wall_height // 2)
            
            for row in range(y0, y1):
                line = screen[row]
                
                # Apply SSAO to wall character
                ssao_factor = self.gfx.calculate_ssao(screen, sc, row)
                if ssao_factor < 0.7:
                    # Darken character in occluded areas
                    if ch == '█': ch = '▓'
                    elif ch == '▓': ch = '▒'
                    elif ch == '▒': ch = '░'
                
                screen[row] = line[:sc] + ch + line[sc+1:]

        # 5. Enhanced object rendering
        screen = self._render_enhanced_objects(screen, world, enemies)
        
        # 6. Next-gen particle system
        screen = self.gfx.render_particles_3d(screen, self.player.x, self.player.y, self.player.angle, self.fov, self.width)

        # 7. POST-PROCESSING PIPELINE:
        
        # Apply bloom effect
        screen = self.gfx.apply_bloom(screen)
        
        # Apply motion blur
        screen = self.gfx.apply_motion_blur(screen, self.player_velocity)
        
        # Apply depth of field
        screen = self.gfx.apply_depth_of_field(screen, self.gfx.dof_focus)
        
        # Apply chromatic aberration
        screen = self.gfx.apply_chromatic_aberration(screen)

        # 8. UI overlays (unaffected by post-processing)
        screen = self._render_minimap(screen, world, enemies)

        if self.weapon_overlay_enabled:
            self._overlay_weapon_next_gen(screen)
            
        return screen

    def _render_enhanced_objects(self, screen: List[str], world: World, enemies: List) -> List[str]:
        """Render pickups, enemies, and projectiles with enhanced effects"""
        
        # Enhanced pickups with glow
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
                    sym = p.symbol()[0]
                    
                    # Add subtle glow for important items
                    if p.kind == 'keycard':
                        for offset in [-1, 0, 1]:
                            if 0 <= sx + offset < self.width:
                                line = screen[sy]
                                glow_char = '·' if offset != 0 else sym
                                screen[sy] = line[:sx + offset] + glow_char + line[sx + offset + 1:]
                    else:
                        line = screen[sy]
                        screen[sy] = line[:sx] + sym + line[sx+1:]

        # Enhanced enemies with subsurface scattering
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
                    
                    # Subsurface scattering - enemies glow from within
                    if hasattr(enemy, 'health') and enemy.health < 30:
                        # Damaged enemies have inner glow
                        for dy in [-1, 0, 1]:
                            if 0 <= sy + dy < len(screen):
                                line = screen[sy + dy]
                                glow_char = '░' if dy != 0 else sprite[0]
                                screen[sy + dy] = line[:sx] + glow_char + line[sx+1:]
                    else:
                        line = screen[sy]
                        screen[sy] = line[:sx] + sprite[0] + line[sx+1:]
        
        # Enhanced projectile rendering
        screen = self._render_enhanced_projectiles(screen, enemies)
        
        return screen

    def _render_enhanced_projectiles(self, screen: List[str], enemies: List) -> List[str]:
        """Render projectiles with enhanced effects"""
        
        # Enhanced enemy bullets with trails
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
                        # Enhanced bullet with glow
                        line = screen[sy]
                        screen[sy] = line[:sx] + '•' + line[sx+1:]
                        
                        # Bullet trail
                        if sx > 0:
                            trail_line = screen[sy]
                            screen[sy] = trail_line[:sx-1] + '·' + trail_line[sx:]
        
        # Enhanced player rockets with advanced trails
        for proj in self.projectiles:
            if not proj.get('alive', True):
                continue
            
            # Enhanced smoke trail
            self.gfx.spawn_smoke_trail(proj['x'], proj['y'])
            
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
                    # Enhanced rocket with glow
                    for offset in [-1, 0, 1]:
                        if 0 <= sx + offset < self.width:
                            line = screen[sy]
                            rocket_char = 'O' if offset == 0 else '·'
                            screen[sy] = line[:sx + offset] + rocket_char + line[sx + offset + 1:]
        
        return screen

    def _overlay_weapon_next_gen(self, screen: List[str]):
        """Enhanced weapon overlay with effects"""
        gun = [
            "      __",
            " ___ /__\\____",
            "|___]__________)"
        ]
        
        # Enhanced muzzle flash with multi-frame animation
        if self.muzzle_flash_ttl > 0:
            flash_chars = ['★', '☆', '✨', '✴', '✵']
            flash_idx = (self.muzzle_flash_frames - self.muzzle_flash_ttl) % len(flash_chars)
            gun[2] = gun[2] + f" {flash_chars[flash_idx]}"
            
            # Add weapon smoke
            if self.muzzle_flash_ttl == 1:
                self.gfx.spawn_smoke_trail(self.width - 8, self.height - 1)
        
        base_row = self.height - len(gun)
        for i, row in enumerate(gun):
            y = base_row + i
            if 0 <= y < self.height:
                start = max(0, self.width - len(row) - 2)
                line = screen[y]
                row = row[:self.width - start]
                screen[y] = line[:start] + row + line[start+len(row):]

    def move_player(self, key: str):
        self.visited.add((int(self.player.x), int(self.player.y)))
        
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
        
        self.visited.add((int(self.player.x), int(self.player.y)))

    def _hitscan_next_gen(self, enemies: List, damage: int, aim_tol: float) -> bool:
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
            
            # Enhanced hit effects
            self.gfx.spawn_sparks(hit_enemy.x, hit_enemy.y, 4)
            self.gfx.spawn_blood(hit_enemy.x, hit_enemy.y, 3)
            
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
            return self._hitscan_next_gen(enemies, dmg, tol)
        elif mode == 'shotgun':
            pellets = int(gp.get('shotgun_pellets', 5))
            spread = float(gp.get('shotgun_spread', 0.2))
            dmg = int(gp.get('shotgun_damage', 12))
            tol = float(gp.get('aim_tolerance', 0.3))
            hit = False
            base_angle = self.player.angle
            for i in range(pellets):
                self.player.angle = base_angle + random.uniform(-spread, spread)
                hit = self._hitscan_next_gen(enemies, dmg, tol) or hit
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
                
                # ULTIMATE explosion effects
                self.gfx.spawn_debris(proj['x'], proj['y'], 15)
                self.gfx.spawn_sparks(proj['x'], proj['y'], 8)
                
                for e in enemies:
                    if getattr(e, 'alive', False):
                        d = math.hypot(e.x - proj['x'], e.y - proj['y'])
                        if d <= radius:
                            e.take_damage(damage)
                            self.gfx.spawn_blood(e.x, e.y, 6)
                            self.gfx.spawn_sparks(e.x, e.y, 5)
                            
                if self.banner_cb:
                    self.banner_cb('BOOM!')

    def update_enemy_bullets(self, enemies: List) -> bool:
        player_hit = False
        damage_angle = None
        
        for enemy in enemies:
            if not hasattr(enemy, 'projectiles'):
                continue
            
            for bullet in enemy.projectiles[:]:
                if not bullet.get('alive'):
                    continue
                    
                bullet['x'] += bullet['dx']
                bullet['y'] += bullet['dy']
                
                if not self._can_move_to(bullet['x'], bullet['y']):
                    bullet['alive'] = False
                    continue
                
                if abs(bullet['x'] - self.player.x) < 0.3 and abs(bullet['y'] - self.player.y) < 0.3:
                    bullet['alive'] = False
                    ai_cfg = self.cfg.get('ai', {})
                    damage = int(ai_cfg.get('bullet_damage', 15))
                    self.player.take_damage(damage)
                    
                    damage_angle = math.atan2(bullet['dy'], bullet['dx'])
                    player_hit = True
                    
                    # Enhanced player hit effects
                    self.gfx.spawn_sparks(self.player.x, self.player.y, 4)
                    self.gfx.spawn_blood(self.player.x, self.player.y, 2)
                    
                    self.damage_feedback()
                    if self.damage_direction_cb:
                        self.damage_direction_cb(damage_angle)
        
        return player_hit

    def _can_move_to(self, x: float, y: float) -> bool:
        return True

    def try_pickups(self, world: World):
        if not hasattr(world, 'pickups') or not world.pickups:
            return
        for p in world.pickups:
            if p.taken:
                continue
            if abs(p.x - self.player.x) < 0.5 and abs(p.y - self.player.y) < 0.5:
                p.taken = True
                # Enhanced pickup effects
                self.gfx.spawn_sparks(p.x, p.y, 2)
                
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
    
    # Compatibility aliases
    def render_3d(self, world: World, enemies: List = None) -> List[str]:
        return self.render_3d_next_gen(world, enemies)
    
    def render_enemies(self, screen: List[str], enemies: List) -> List[str]:
        return screen  # Integrated into main pipeline
    
    def render_enemy_bullets(self, screen: List[str], enemies: List) -> List[str]:
        return screen  # Integrated into main pipeline

# Compatibility alias
RaycastingEngine = UltimateRaycastingEngine