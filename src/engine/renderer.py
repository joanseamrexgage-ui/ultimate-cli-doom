"""
GODLIKE ASCII GRAPHICS Renderer
Reality-bending visual effects that transcend ASCII limitations
"""

import math
import os
import random
from typing import List, Tuple
from ..core.player import Player
from ..core.world import World
from .graphics_fx import NextGenGraphicsFX
from .godlike_fx import GodlikeGraphicsFX

try:
    import tomllib as toml
except Exception:
    toml = None

WALKABLE = {'.', '·', '~', ' '}

# GODLIKE wall material mappings with quantum properties
GODLIKE_MATERIALS = {
    'stone': {
        'symbols': ['▒', '▓', '█'], 
        'base': '▒',
        'reflectivity': 0.1,
        'roughness': 0.8,
        'parallax_scale': 0.3,
        'quantum_resonance': 0.0,
        'hologram_opacity': 0.0
    },
    'brick': {
        'symbols': ['░', '▒', '▓'], 
        'base': '░',
        'reflectivity': 0.05,
        'roughness': 0.9,
        'parallax_scale': 0.4,
        'quantum_resonance': 0.1,
        'hologram_opacity': 0.0
    },  
    'metal': {
        'symbols': ['█', '▓', '▒'], 
        'base': '█',
        'reflectivity': 0.9,
        'roughness': 0.1,
        'parallax_scale': 0.1,
        'quantum_resonance': 0.8,
        'hologram_opacity': 0.3
    },
    'wood': {
        'symbols': ['║', '│', '┃'], 
        'base': '║',
        'reflectivity': 0.0,
        'roughness': 0.7,
        'parallax_scale': 0.5,
        'quantum_resonance': 0.2,
        'hologram_opacity': 0.0
    },
    'quantum_crystal': {
        'symbols': ['◆', '◇', '◈', '◉', '◊'], 
        'base': '◆',
        'reflectivity': 1.0,
        'roughness': 0.0,
        'parallax_scale': 0.0,
        'quantum_resonance': 1.0,
        'hologram_opacity': 0.7
    }
}

class GodlikeRaycastingEngine:
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
        
        # Navigation aids (always enabled)
        self.minimap_enabled = bool(g.get('minimap_enabled', True))
        self.minimap_width = int(g.get('minimap_width', 15))
        self.minimap_height = int(g.get('minimap_height', 8))
        self.materials_enabled = bool(g.get('materials_enabled', True))
        
        # Initialize GODLIKE graphics systems
        self.gfx = NextGenGraphicsFX(self.cfg)
        self.godlike = GodlikeGraphicsFX(self.cfg)
        
        # Enhanced tracking
        self.visited = set()
        self.player_velocity = 0.0
        self.last_player_pos = (0.0, 0.0)
        self.sound_events = []  # For sound visualization
        self.critical_effects_active = False
        
        self.player = Player(x=1.5, y=1.5, angle=0)
        self.shake_ttl = 0
        self.muzzle_flash_ttl = 0
        self.projectiles = []
        self.banner_cb = None
        self.flash_cb = None
        self.damage_direction_cb = None

    def _apply_shake(self, x: int) -> int:
        # Enhanced shake with reality distortion
        base_shake = 0
        if self.camera_shake and self.shake_ttl > 0:
            base_shake = random.randint(-self.shake_strength, self.shake_strength)
        
        # Add quantum instability
        if self.godlike.reality_glitch and random.random() < 0.05:
            base_shake += random.randint(-2, 2)
        
        return max(0, min(self.width - 1, x + base_shake))

    def damage_feedback(self):
        self.shake_ttl = self.shake_frames
        
        # Spawn reality glitch on damage
        self.godlike.spawn_reality_glitch(int(self.player.x), int(self.player.y), 2)
        
        if self.flash_cb:
            self.flash_cb()

    def muzzle_flash(self):
        self.muzzle_flash_ttl = self.muzzle_flash_frames
        
        # Add sound visualization for gunshot
        self.sound_events.append((int(self.player.x), int(self.player.y), 'gunshot'))

    def _get_godlike_material_char(self, wall_type: str, distance: float, world: World, hit_x: int, hit_y: int, angle: float) -> str:
        """GODLIKE material rendering with quantum effects"""
        if not self.materials_enabled:
            return self._shade(distance)
            
        # Determine material with quantum enhancements
        material = getattr(world, 'material', 'stone')
        if hasattr(world, 'theme'):
            material_map = {
                'quantum': 'quantum_crystal',  # Upgraded!
                'atman': 'stone', 
                'loqiemean': 'brick',
                'batut': 'wood'
            }
            material = material_map.get(world.theme, 'stone')
        
        if distance >= self.max_depth:
            return ' '
            
        mat_data = GODLIKE_MATERIALS.get(material, GODLIKE_MATERIALS['stone'])
        symbols = mat_data['symbols']
        
        # GODLIKE SHADER PIPELINE:
        
        # 1. Base distance calculation
        t = min(0.99, distance / self.max_depth)
        
        # 2. Quantum resonance effects
        if mat_data['quantum_resonance'] > 0 and self.godlike.hologram_projection:
            quantum_wave = math.sin(self.godlike.tick * 0.1 + hit_x * 0.3 + hit_y * 0.2)
            quantum_factor = quantum_wave * mat_data['quantum_resonance']
            t = max(0, t - quantum_factor * 0.3)
        
        # 3. Enhanced lighting with emotion
        emotion_palette = self.godlike.get_emotion_palette(symbols)
        light_intensity = self.gfx.get_enhanced_light_intensity(hit_x, hit_y, world.map if hasattr(world, 'map') else None)
        
        # 4. Apply hologram flickering
        if mat_data['hologram_opacity'] > 0:
            flicker = math.sin(self.godlike.tick * 0.15) * 0.5 + 0.5
            if flicker < mat_data['hologram_opacity']:
                # Holographic transparency
                return '◦' if random.random() < 0.5 else ' '
        
        # 5. Advanced parallax with quantum distortion
        parallax_offset = 0
        if abs(angle) < math.pi/4:
            view_angle = abs(angle)
            parallax_offset = int(view_angle * mat_data['parallax_scale'] * 2)
            
            # Add quantum instability to parallax
            if mat_data['quantum_resonance'] > 0.5:
                quantum_jitter = math.sin(self.godlike.tick * 0.2 + hit_x + hit_y) * mat_data['quantum_resonance']
                parallax_offset += int(quantum_jitter)
        
        # 6. Time dilation effects
        time_factor = self.godlike.get_effect_multiplier()
        if time_factor < 0.8:
            t = t * (1.5 - time_factor)  # Slow motion enhances detail
        
        # 7. Final character selection with all effects
        t = max(0, t / light_intensity)
        
        if self.muzzle_flash_ttl > 0 and t < 0.3:
            t = max(0, t - self.muzzle_flash_brightness * 0.1)
        
        idx = max(0, min(len(emotion_palette) - 1, int(t * (len(emotion_palette) - 1)) + parallax_offset))
        return emotion_palette[idx]

    def render_3d_godlike(self, world: World, enemies: List = None) -> List[str]:
        """GODLIKE rendering pipeline that transcends reality"""
        if enemies is None:
            enemies = []
        
        # Update player state tracking
        current_pos = (self.player.x, self.player.y)
        self.player_velocity = math.hypot(
            current_pos[0] - self.last_player_pos[0],
            current_pos[1] - self.last_player_pos[1]
        )
        self.last_player_pos = current_pos
        
        # Record ghost trail
        self.godlike.record_player_ghost(self.player.x, self.player.y)
        
        # Update critical state
        self.critical_effects_active = self.player.health < 30
        
        if self.shake_ttl > 0:
            self.shake_ttl -= 1
        if self.muzzle_flash_ttl > 0:
            self.muzzle_flash_ttl -= 1

        # Update all graphics systems
        self.gfx.update()
        self.godlike.update(self.player.health, self.player_velocity)
        self.gfx.update_light_sources(world.map)
        self.godlike.initialize_living_walls(world.map)

        # Initialize screen
        screen = [' ' * self.width for _ in range(self.height)]
        sky_height = self.height // 2
        
        # GODLIKE RENDER PIPELINE:
        
        # 1. Reality-bending sky
        theme = getattr(world, 'theme', 'quantum')
        screen = self.gfx.render_enhanced_sky(screen, self.width, sky_height, theme)
        
        # Matrix rain effect when critical
        if self.critical_effects_active and self.godlike.matrix_rain:
            self.godlike.spawn_matrix_rain(self.width, 15)
        
        # 2. Volumetric lighting with quantum fields
        screen = self.gfx.render_volumetric_lighting(screen, self.width, self.height, world.map)

        # 3. Enhanced floor with living elements
        for y in range(self.height // 2, self.height):
            floor_line = ''
            floor_chars = [self.floor_char]
            
            # Theme-specific living floors
            if hasattr(world, 'theme'):
                theme_floors = {
                    'quantum': ['.', '·', '¨', '⋅', '◆'],  # Crystals can grow
                    'atman': ['·', '∘', '°', '◦', '♥'],     # Organic life
                    'loqiemean': ['~', '≈', '∼', '〜', '○'], # Flowing water
                    'batut': [' ', '·', '`', '‵', '┤']       # Root systems
                }
                floor_chars = theme_floors.get(world.theme, [self.floor_char])
            
            for x in range(self.width):
                # Enhanced procedural floor with growth
                base_chance = 0.12
                
                # Living floor growth in certain biomes
                if self.godlike.growing_crystals and theme == 'quantum':
                    crystal_growth = math.sin(x * 0.1 + y * 0.05 + self.godlike.tick * 0.02)
                    if crystal_growth > 0.8:
                        floor_line += '◆'
                        continue
                
                # SSAO-enhanced variation
                ssao_factor = self.gfx.calculate_ssao(screen, x, y)
                variation_chance = base_chance * ssao_factor
                
                if random.random() < variation_chance:
                    floor_line += random.choice(floor_chars)
                else:
                    floor_line += floor_chars[0]
            screen[y] = floor_line
        
        # Apply fluid layer
        screen = self.gfx.render_fluid_layer(screen, world.map)

        # 4. GODLIKE WALL RENDERING with reality distortion
        for col in range(self.width):
            sc = self._apply_shake(col)
            ray_angle = (self.player.angle - self.fov / 2 + col / self.width * self.fov)
            distance, wall_type, hit_x, hit_y, surface_normal = self.cast_ray_next_gen(ray_angle, world.map)
            cd = self.correct_fish_eye(distance, ray_angle)
            wall_height = self.height if cd <= 0.1 else min(self.height, int(self.height / cd))
            
            # GODLIKE material character
            ch = self._get_godlike_material_char(wall_type, cd, world, hit_x, hit_y, surface_normal)
            
            y0 = max(0, self.height // 2 - wall_height // 2)
            y1 = min(self.height, self.height // 2 + wall_height // 2)
            
            for row in range(y0, y1):
                line = screen[row]
                
                # Enhanced SSAO with quantum interference
                ssao_factor = self.gfx.calculate_ssao(screen, sc, row)
                if self.godlike.reality_glitch and random.random() < 0.01:
                    ssao_factor *= random.uniform(0.5, 1.5)  # Reality distortion
                
                if ssao_factor < 0.7:
                    if ch == '█': ch = '▓'
                    elif ch == '▓': ch = '▒'
                    elif ch == '▒': ch = '░'
                
                screen[row] = line[:sc] + ch + line[sc+1:]

        # 5. GODLIKE object and entity rendering
        screen = self._render_godlike_objects(screen, world, enemies)
        
        # 6. Advanced particle systems with quantum effects
        screen = self.gfx.render_particles_3d(screen, self.player.x, self.player.y, self.player.angle, self.fov, self.width)

        # 7. GODLIKE POST-PROCESSING PIPELINE:
        
        # Apply living wall effects
        screen = self.godlike.apply_living_wall_effects(screen, world.map, theme)
        
        # Apply quantum field distortions
        screen = self.godlike.apply_quantum_field_effects(screen)
        
        # Sound wave visualization
        if self.sound_events:
            screen = self.godlike.apply_sound_visualization(screen, self.sound_events)
            self.sound_events.clear()
        
        # Electromagnetic field effects for metal objects
        metal_objects = [(int(self.player.x), int(self.player.y))]  # Player has metal weapon
        screen = self.godlike.apply_electromagnetic_effects(screen, metal_objects)
        
        # Thermal imaging overlay
        screen = self.godlike.apply_thermal_imaging(screen, enemies)
        
        # Time dilation visual effects
        screen = self.godlike.apply_time_dilation_effects(screen)
        
        # Rewind ghost trail
        screen = self.godlike.render_rewind_ghosts(screen, self.player.x, self.player.y)
        
        # AI upscaling and procedural detail
        screen = self.godlike.apply_ai_upscaling(screen)
        screen = self.godlike.apply_procedural_detail_generation(screen, 0.3)
        
        # Standard post-processing
        screen = self.gfx.apply_bloom(screen)
        screen = self.gfx.apply_motion_blur(screen, self.player_velocity)
        screen = self.gfx.apply_depth_of_field(screen, self.gfx.dof_focus)
        screen = self.gfx.apply_chromatic_aberration(screen)

        # 8. UI overlays (protected from effects)
        screen = self._render_enhanced_minimap(screen, world, enemies)

        if self.weapon_overlay_enabled:
            self._overlay_godlike_weapon(screen)
            
        return screen

    def _render_godlike_objects(self, screen: List[str], world: World, enemies: List) -> List[str]:
        """Render objects with godlike effects"""
        
        # Enhanced pickups with holographic projection
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
                    
                    # Hologram projection for key items
                    if p.kind == 'keycard' and self.godlike.hologram_projection:
                        self.godlike.spawn_hologram_projection(sx, sy, 120)
                        # Multi-state keycard rendering
                        hologram_chars = ['★', '☆', '✨', sym]
                        hologram_phase = (self.godlike.tick // 5) % len(hologram_chars)
                        sym = hologram_chars[hologram_phase]
                    
                    # Quantum glow for important items
                    if p.kind in ['keycard', 'health']:
                        for offset in [-1, 0, 1]:
                            if 0 <= sx + offset < self.width:
                                line = screen[sy]
                                glow_char = '◦' if offset != 0 else sym
                                screen[sy] = line[:sx + offset] + glow_char + line[sx + offset + 1:]
                    else:
                        line = screen[sy]
                        screen[sy] = line[:sx] + sym + line[sx+1:]

        # GODLIKE enemies with quantum tunneling and subsurface scattering
        for enemy in enemies:
            if not getattr(enemy, 'alive', False):
                continue
            
            # Check for teleportation/special abilities
            if hasattr(enemy, 'is_teleporting') and enemy.is_teleporting:
                self.godlike.enable_quantum_tunneling(int(enemy.x), int(enemy.y))
            
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
                    
                    # Advanced enemy rendering with multiple effects
                    if hasattr(enemy, 'health') and enemy.health < 30:
                        # Damaged enemies: subsurface + reality distortion
                        for dy in [-1, 0, 1]:
                            if 0 <= sy + dy < len(screen):
                                line = screen[sy + dy]
                                if dy == 0:
                                    # Main sprite with potential quantum effect
                                    if random.random() < 0.1:
                                        sprite = '█' if random.random() < 0.5 else sprite[0]
                                    screen[sy + dy] = line[:sx] + sprite[0] + line[sx+1:]
                                else:
                                    # Subsurface glow
                                    glow_char = '◦' if enemy.health < 15 else '░'
                                    screen[sy + dy] = line[:sx] + glow_char + line[sx+1:]
                    else:
                        line = screen[sy]
                        screen[sy] = line[:sx] + sprite[0] + line[sx+1:]
        
        # Enhanced projectiles with quantum effects
        screen = self._render_godlike_projectiles(screen, enemies)
        
        return screen

    def _render_godlike_projectiles(self, screen: List[str], enemies: List) -> List[str]:
        """Render projectiles with reality-bending effects"""
        
        # Enhanced enemy bullets with electromagnetic trails
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
                        # Quantum bullet with electromagnetic trail
                        bullet_chars = ['•', '●', '◉', '★']
                        bullet_phase = (self.godlike.tick // 3) % len(bullet_chars)
                        
                        line = screen[sy]
                        screen[sy] = line[:sx] + bullet_chars[bullet_phase] + line[sx+1:]
                        
                        # Electromagnetic trail
                        if self.godlike.electromagnetic_fields and sx > 0:
                            trail_line = screen[sy]
                            screen[sy] = trail_line[:sx-1] + '~' + trail_line[sx:]
        
        # GODLIKE player rockets with time distortion
        for proj in self.projectiles:
            if not proj.get('alive', True):
                continue
            
            # Enhanced quantum smoke trail
            self.gfx.spawn_smoke_trail(proj['x'], proj['y'])
            if self.godlike.time_effects and self.godlike.time_dilation < 0.7:
                # Bullet time - extra smoke
                self.gfx.spawn_smoke_trail(proj['x'] - proj['dx'] * 0.5, proj['y'] - proj['dy'] * 0.5)
            
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
                    # Quantum-enhanced rocket
                    rocket_chars = ['O', '○', '◉', '★']
                    rocket_phase = (self.godlike.tick // 2) % len(rocket_chars)
                    
                    # Time dilation effect - rocket appears larger when slowed
                    if self.godlike.time_dilation < 0.6:
                        for offset in [-2, -1, 0, 1, 2]:
                            if 0 <= sx + offset < self.width:
                                line = screen[sy]
                                if offset == 0:
                                    char = rocket_chars[rocket_phase]
                                else:
                                    char = '·'
                                screen[sy] = line[:sx + offset] + char + line[sx + offset + 1:]
                    else:
                        line = screen[sy]
                        screen[sy] = line[:sx] + rocket_chars[rocket_phase] + line[sx+1:]
        
        return screen

    def _render_enhanced_minimap(self, screen: List[str], world: World, enemies: List) -> List[str]:
        """Enhanced minimap with quantum visualization"""
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
                
                # GODLIKE minimap symbols with quantum effects
                if abs(mx - px) < 1 and abs(my - py) < 1:
                    # Player with quantum aura when critical
                    if self.critical_effects_active:
                        player_chars = ['◎', '◉', '◊', '○']
                        char = player_chars[(self.godlike.tick // 4) % len(player_chars)]
                    else:
                        char = '◎'
                
                elif any(abs(e.x - mx - 0.5) < 1 and abs(e.y - my - 0.5) < 1 
                        and getattr(e, 'alive', False) for e in enemies):
                    # Enemies with thermal signature
                    if self.godlike.thermal_imaging:
                        thermal_chars = ['⚠', '◉', '★']
                        char = thermal_chars[(self.godlike.tick // 6) % len(thermal_chars)]
                    else:
                        char = '⚠'
                
                elif world.map[my][mx] not in WALKABLE:
                    # Walls with living indication
                    if (mx, my) in self.godlike.wall_entities:
                        char = '■' if (self.godlike.tick // 8) % 2 else '□'
                    else:
                        char = '■'
                else:
                    char = '·'
                
                screen[screen_y] = line[:screen_x] + char + line[screen_x + 1:]
        
        return screen

    def _overlay_godlike_weapon(self, screen: List[str]):
        """Enhanced weapon overlay with quantum effects"""
        gun = [
            "      __",
            " ___ /__\\____",
            "|___]__________)"
        ]
        
        # GODLIKE muzzle flash with reality distortion
        if self.muzzle_flash_ttl > 0:
            flash_chars = ['★', '☆', '✨', '✴', '✵', '✿', '❀']
            flash_idx = (self.muzzle_flash_frames - self.muzzle_flash_ttl) % len(flash_chars)
            
            # Quantum muzzle flash
            if self.godlike.quantum_tunneling:
                quantum_flash = ['◆', '◇', '◈', '◉', '◊']
                flash_char = quantum_flash[self.godlike.tick % len(quantum_flash)]
            else:
                flash_char = flash_chars[flash_idx]
            
            gun[2] = gun[2] + f" {flash_char}"
            
            # Reality distortion around weapon
            if self.godlike.reality_glitch:
                self.godlike.spawn_reality_glitch(self.width - 10, self.height - 2, 1)
        
        base_row = self.height - len(gun)
        for i, row in enumerate(gun):
            y = base_row + i
            if 0 <= y < self.height:
                start = max(0, self.width - len(row) - 2)
                line = screen[y]
                
                # Apply weapon breathing effect if enabled
                if self.godlike.living_walls and (self.godlike.tick % 20) < 10:
                    row = row.replace('_', '‾')  # Subtle breathing
                
                row = row[:self.width - start]
                screen[y] = line[:start] + row + line[start+len(row):]

    # Compatibility methods with enhanced functionality
    def cast_ray_next_gen(self, angle: float, world_map: List[str]) -> Tuple[float, str, int, int, float]:
        """GODLIKE ray casting with reality bending"""
        ox = self.player.x
        oy = self.player.y
        dx = math.cos(angle)
        dy = math.sin(angle)
        step = 0.01  # Ultra-high precision
        dist = 0.0
        hit_x, hit_y = 0, 0
        surface_normal = 0.0
        
        # Quantum tunneling can affect ray casting
        tunneling_chance = 0.01 if self.godlike.quantum_tunneling else 0.0
        
        while dist < self.max_depth:
            ox += dx * step
            oy += dy * step
            dist += step
            mx, my = int(ox), int(oy)
            
            # Enhanced visited tracking with quantum uncertainty
            if 0 <= mx < 100 and 0 <= my < 100:
                self.visited.add((mx, my))
                # Quantum uncertainty - sometimes reveal adjacent cells
                if self.godlike.quantum_tunneling and random.random() < 0.05:
                    for dx_q in [-1, 0, 1]:
                        for dy_q in [-1, 0, 1]:
                            self.visited.add((mx + dx_q, my + dy_q))
            
            if my < 0 or my >= len(world_map) or mx < 0 or mx >= len(world_map[0]):
                return self.max_depth, 'void', mx, my, 0.0
            
            if world_map[my][mx] not in WALKABLE:
                # Quantum tunneling - small chance to pass through
                if random.random() < tunneling_chance:
                    continue
                
                surface_normal = math.atan2(my - self.player.y, mx - self.player.x)
                return dist, world_map[my][mx], mx, my, surface_normal
            
            hit_x, hit_y = mx, my
            
        return self.max_depth, 'void', hit_x, hit_y, surface_normal

    def move_player(self, key: str):
        """Enhanced player movement with quantum effects"""
        self.visited.add((int(self.player.x), int(self.player.y)))
        
        speed = float(self.cfg.get('gameplay', {}).get('player_speed', 0.2))
        rot = float(self.cfg.get('gameplay', {}).get('rotate_speed', 0.2))
        
        # Time dilation affects movement
        speed *= self.godlike.get_effect_multiplier()
        rot *= self.godlike.get_effect_multiplier()
        
        if key == 'w':
            dx = speed * math.cos(self.player.angle)
            dy = speed * math.sin(self.player.angle)
            self.player.move(dx, dy)
            # Add footstep sound
            self.sound_events.append((int(self.player.x), int(self.player.y), 'footstep'))
        elif key == 's':
            dx = -speed * math.cos(self.player.angle)
            dy = -speed * math.sin(self.player.angle)
            self.player.move(dx, dy)
        elif key == 'a':
            self.player.rotate(-rot)
        elif key == 'd':
            self.player.rotate(rot)
        
        self.visited.add((int(self.player.x), int(self.player.y)))

    def update_projectiles(self, world: World, enemies: List):
        """Enhanced projectile update with godlike explosion effects"""
        gp = self.cfg.get('gameplay', {})
        radius = float(gp.get('rocket_radius', 1.2))
        damage = int(gp.get('rocket_damage', 40))
        
        for proj in self.projectiles:
            if not proj.get('alive', True):
                continue
                
            # Time dilation affects projectile speed
            time_factor = self.godlike.get_effect_multiplier()
            proj['x'] += proj['dx'] * time_factor
            proj['y'] += proj['dy'] * time_factor
            
            mx, my = int(proj['x']), int(proj['y'])
            if my < 0 or my >= len(world.map) or mx < 0 or mx >= len(world.map[0]) or world.map[my][mx] not in WALKABLE:
                proj['alive'] = False
                
                # GODLIKE explosion effects
                self.gfx.spawn_debris(proj['x'], proj['y'], 20)
                self.gfx.spawn_sparks(proj['x'], proj['y'], 12)
                
                # Reality distortion from explosion
                self.godlike.spawn_reality_glitch(int(proj['x']), int(proj['y']), 4)
                
                # Sound wave visualization
                self.sound_events.append((int(proj['x']), int(proj['y']), 'explosion'))
                
                for e in enemies:
                    if getattr(e, 'alive', False):
                        d = math.hypot(e.x - proj['x'], e.y - proj['y'])
                        if d <= radius:
                            e.take_damage(damage)
                            self.gfx.spawn_blood(e.x, e.y, 8)
                            self.gfx.spawn_sparks(e.x, e.y, 6)
                            
                if self.banner_cb:
                    self.banner_cb('QUANTUM BOOM!')

    # Compatibility aliases
    def render_3d(self, world: World, enemies: List = None) -> List[str]:
        return self.render_3d_godlike(world, enemies)
    
    def correct_fish_eye(self, d: float, a: float) -> float:
        return d * math.cos(a - self.player.angle)
    
    def _shade(self, distance: float) -> str:
        if distance >= self.max_depth:
            return ' '
        t = distance / self.max_depth
        if self.muzzle_flash_ttl > 0 and t < 0.3:
            t = max(0, t - self.muzzle_flash_brightness * 0.1)
        idx = int(t * (len(self.palette) - 1))
        return self.palette[idx]

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
            return self._hitscan_godlike(enemies, dmg, tol)
        elif mode == 'shotgun':
            pellets = int(gp.get('shotgun_pellets', 5))
            spread = float(gp.get('shotgun_spread', 0.2))
            dmg = int(gp.get('shotgun_damage', 12))
            tol = float(gp.get('aim_tolerance', 0.3))
            hit = False
            base_angle = self.player.angle
            for i in range(pellets):
                self.player.angle = base_angle + random.uniform(-spread, spread)
                hit = self._hitscan_godlike(enemies, dmg, tol) or hit
            self.player.angle = base_angle
            return hit
        elif mode == 'rocket':
            speed = float(gp.get('rocket_speed', 0.6))
            dx = math.cos(self.player.angle) * speed
            dy = math.sin(self.player.angle) * speed
            self.projectiles.append({'x': self.player.x, 'y': self.player.y, 'dx': dx, 'dy': dy, 'alive': True})
            return True
        return False

    def _hitscan_godlike(self, enemies: List, damage: int, aim_tol: float) -> bool:
        """Enhanced hitscan with quantum effects"""
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
            
            # GODLIKE hit effects
            self.gfx.spawn_sparks(hit_enemy.x, hit_enemy.y, 6)
            self.gfx.spawn_blood(hit_enemy.x, hit_enemy.y, 4)
            
            # Quantum resonance effect
            if self.godlike.hologram_projection:
                self.godlike.spawn_hologram_projection(int(hit_enemy.x), int(hit_enemy.y), 30)
            
            return True
        return False

    def update_enemy_bullets(self, enemies: List) -> bool:
        """Enhanced bullet update with quantum effects"""
        player_hit = False
        
        for enemy in enemies:
            if not hasattr(enemy, 'projectiles'):
                continue
            
            for bullet in enemy.projectiles[:]:
                if not bullet.get('alive'):
                    continue
                
                # Time dilation affects bullet speed
                time_factor = self.godlike.get_effect_multiplier()
                bullet['x'] += bullet['dx'] * time_factor
                bullet['y'] += bullet['dy'] * time_factor
                
                if not self._can_move_to(bullet['x'], bullet['y']):
                    bullet['alive'] = False
                    continue
                
                if abs(bullet['x'] - self.player.x) < 0.3 and abs(bullet['y'] - self.player.y) < 0.3:
                    bullet['alive'] = False
                    ai_cfg = self.cfg.get('ai', {})
                    damage = int(ai_cfg.get('bullet_damage', 15))
                    self.player.take_damage(damage)
                    
                    player_hit = True
                    
                    # GODLIKE player hit effects
                    self.gfx.spawn_sparks(self.player.x, self.player.y, 5)
                    self.gfx.spawn_blood(self.player.x, self.player.y, 3)
                    self.godlike.spawn_reality_glitch(int(self.player.x), int(self.player.y), 2)
                    
                    self.damage_feedback()
        
        return player_hit

    def try_pickups(self, world: World):
        """Enhanced pickup with quantum effects"""
        if not hasattr(world, 'pickups') or not world.pickups:
            return
        for p in world.pickups:
            if p.taken:
                continue
            if abs(p.x - self.player.x) < 0.5 and abs(p.y - self.player.y) < 0.5:
                p.taken = True
                
                # GODLIKE pickup effects
                self.gfx.spawn_sparks(p.x, p.y, 4)
                if p.kind == 'keycard':
                    self.godlike.spawn_hologram_projection(int(p.x), int(p.y), 60)
                
                if p.kind == 'health':
                    self.player.heal(p.amount)
                    if self.banner_cb:
                        self.banner_cb('Quantum healing acquired')
                elif p.kind == 'ammo':
                    self.player.add_ammo(p.amount)
                    if self.banner_cb:
                        self.banner_cb('Energy cells loaded')
                elif p.kind == 'keycard':
                    if self.banner_cb:
                        self.banner_cb('Reality key acquired')

    def _can_move_to(self, x: float, y: float) -> bool:
        return True

    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

# Compatibility aliases
RaycastingEngine = GodlikeRaycastingEngine
UltimateRaycastingEngine = GodlikeRaycastingEngine