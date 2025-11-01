"""
🎨 ULTIMATE NEXT-GEN ASCII Graphics FX System
Revolutionary visual effects for CLI gaming
"""

import math
import random
from typing import List, Tuple, Dict, Set

class Particle:
    def __init__(self, x: float, y: float, dx: float, dy: float, char: str, ttl: int, p_type: str = 'generic'):
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.char = char
        self.ttl = ttl
        self.max_ttl = ttl
        self.type = p_type  # 'spark', 'debris', 'smoke', 'blood', 'magic'
        self.gravity = -0.02 if p_type == 'debris' else -0.01
        self.wind_resistance = 0.98 if p_type == 'smoke' else 0.95
        self.glow = p_type in ['spark', 'magic']
    
    def update(self, wind_x: float = 0, wind_y: float = 0):
        # Wind effects
        self.dx += wind_x * 0.1
        self.dy += wind_y * 0.1
        
        self.x += self.dx
        self.y += self.dy
        
        if self.type == 'debris':
            self.dy += self.gravity
        elif self.type == 'smoke':
            self.dy -= 0.05  # Rise upward
        elif self.type == 'blood':
            self.dx *= 0.9  # Spread and settle
            self.dy *= 0.9
            
        self.dx *= self.wind_resistance
        self.dy *= self.wind_resistance
        self.ttl -= 1
    
    def is_alive(self) -> bool:
        return self.ttl > 0
    
    def get_char(self) -> str:
        fade_ratio = self.ttl / self.max_ttl
        
        if self.type == 'spark':
            if fade_ratio > 0.7: return '*'
            elif fade_ratio > 0.4: return '+'
            elif fade_ratio > 0.1: return '·'
            else: return '`'
        elif self.type == 'blood':
            if fade_ratio > 0.8: return '●'
            elif fade_ratio > 0.5: return '•'
            elif fade_ratio > 0.2: return '·'
            else: return '`'
        elif self.type == 'smoke':
            if fade_ratio > 0.6: return '○'
            elif fade_ratio > 0.3: return '°'
            else: return '·'
        else:
            # Generic fade
            if fade_ratio > 0.6: return self.char
            elif fade_ratio > 0.3: return '·'
            else: return '`'

class FluidCell:
    def __init__(self, x: int, y: int, fluid_type: str = 'blood'):
        self.x = x
        self.y = y
        self.type = fluid_type
        self.density = 1.0
        self.age = 0
        self.evaporation_rate = 0.02 if fluid_type == 'blood' else 0.01
    
    def update(self):
        self.age += 1
        self.density -= self.evaporation_rate
        return self.density > 0.1
    
    def get_char(self) -> str:
        if self.density > 0.8: return '●'
        elif self.density > 0.5: return '•'
        elif self.density > 0.2: return '·'
        else: return '`'

class NextGenGraphicsFX:
    def __init__(self, config: Dict):
        self.config = config.get('graphics', {})
        self.tuning = config.get('graphics', {}).get('tuning', {})
        self.tick = 0
        self.particles = []
        self.fluids = {}  # Dict[(x,y)] = FluidCell
        self.damaged_walls = {}  # Dict[(x,y)] = damage_level
        self.wind = {'x': 0.0, 'y': 0.0, 'strength': 0.0}
        
        # Next-gen feature flags
        self.reflections = bool(self.config.get('reflections', False))
        self.gi_volumetrics = bool(self.config.get('gi_volumetrics', True))
        self.shadows = bool(self.config.get('shadows', False))
        self.ssao = bool(self.config.get('ssao', True))
        self.bloom = bool(self.config.get('bloom', True))
        self.motion_blur = bool(self.config.get('motion_blur', False))
        self.dof = bool(self.config.get('dof', False))
        self.fluids_enabled = bool(self.config.get('fluids', False))
        self.destructibles = bool(self.config.get('destructibles', False))
        self.wind_enabled = bool(self.config.get('wind', False))
        self.chromatic_aberration = bool(self.config.get('chromatic_aberration', False))
        
        # Enhanced animation flags
        self.sky_animated = bool(self.config.get('sky_animated', True))
        self.fog_enabled = bool(self.config.get('fog_enabled', True))
        self.particles_enabled = bool(self.config.get('particles_enabled', True))
        self.lights_enabled = bool(self.config.get('lights_enabled', True))
        
        # Tuning parameters
        self.ray_depth = int(self.tuning.get('ray_depth', 1))
        self.ao_radius = int(self.tuning.get('ao_radius', 1))
        self.bloom_strength = float(self.tuning.get('bloom_strength', 0.3))
        self.blur_strength = float(self.tuning.get('blur_strength', 0.2))
        self.dof_focus = float(self.tuning.get('dof_focus', 5.0))
        
        # Standard parameters
        self.fog_speed = float(self.config.get('fog_speed', 0.8))
        self.fog_intensity = float(self.config.get('fog_intensity', 0.25))
        self.sparks_ttl = int(self.config.get('sparks_ttl', 3))
        self.debris_ttl = int(self.config.get('debris_ttl', 8))
        self.particles_max = int(self.config.get('particles_max', 300))
        self.light_radius = float(self.config.get('light_radius', 3.0))
        self.light_pulse_speed = float(self.config.get('light_pulse_speed', 1.2))
        
        # Cache for optimized rendering
        self.light_sources = []
        self.reflection_cache = {}
        self.shadow_cache = {}

    def update(self):
        """Update all dynamic systems"""
        self.tick += 1
        
        # Update particles with wind
        if self.particles_enabled:
            if self.wind_enabled:
                self._update_wind()
            
            self.particles = [p for p in self.particles if p.is_alive()]
            for p in self.particles:
                p.update(self.wind['x'], self.wind['y'])
        
        # Update fluids
        if self.fluids_enabled:
            self._update_fluids()
    
    def _update_wind(self):
        """Update wind system"""
        # Procedural wind patterns
        wind_phase = self.tick * 0.02
        self.wind['x'] = math.sin(wind_phase) * 0.1
        self.wind['y'] = math.cos(wind_phase * 0.7) * 0.05
        self.wind['strength'] = abs(self.wind['x']) + abs(self.wind['y'])
    
    def _update_fluids(self):
        """Update fluid simulation"""
        to_remove = []
        for pos, fluid in self.fluids.items():
            if not fluid.update():
                to_remove.append(pos)
        
        for pos in to_remove:
            del self.fluids[pos]

    def calculate_ssao(self, screen: List[str], x: int, y: int) -> float:
        """Calculate Screen Space Ambient Occlusion"""
        if not self.ssao or y >= len(screen) or x >= len(screen[0]):
            return 1.0
        
        occlusion = 0.0
        samples = 0
        
        for dy in range(-self.ao_radius, self.ao_radius + 1):
            for dx in range(-self.ao_radius, self.ao_radius + 1):
                nx, ny = x + dx, y + dy
                if 0 <= nx < len(screen[0]) and 0 <= ny < len(screen):
                    if screen[ny][nx] in '█▓▒▓║':  # Dark/wall characters
                        dist = math.hypot(dx, dy)
                        if dist <= self.ao_radius:
                            occlusion += (1.0 - dist / self.ao_radius) * 0.3
                    samples += 1
        
        return max(0.3, 1.0 - occlusion / max(1, samples))

    def apply_bloom(self, screen: List[str]) -> List[str]:
        """Apply bloom effect to bright characters"""
        if not self.bloom:
            return screen
        
        bright_chars = {'*', '★', '☆', '●', '○', '◊', '◆'}
        bloom_screen = [list(row) for row in screen]
        
        for y, row in enumerate(screen):
            for x, char in enumerate(row):
                if char in bright_chars:
                    # Apply bloom in small radius
                    for dy in range(-1, 2):
                        for dx in range(-1, 2):
                            nx, ny = x + dx, y + dy
                            if 0 <= nx < len(row) and 0 <= ny < len(screen):
                                if dx == 0 and dy == 0:
                                    continue
                                # Brighten neighboring characters slightly
                                current = bloom_screen[ny][nx]
                                if current in ' ·`':
                                    bloom_screen[ny][nx] = '·'
                                elif current in '░▒':
                                    bloom_screen[ny][nx] = '▒'
        
        return [''.join(row) for row in bloom_screen]

    def apply_chromatic_aberration(self, screen: List[str]) -> List[str]:
        """Apply subtle chromatic aberration at screen edges"""
        if not self.chromatic_aberration:
            return screen
        
        width = len(screen[0]) if screen else 0
        height = len(screen)
        center_x, center_y = width // 2, height // 2
        
        aberrated = [list(row) for row in screen]
        
        for y in range(height):
            for x in range(width):
                # Calculate distance from center
                dx = x - center_x
                dy = y - center_y
                dist_ratio = math.hypot(dx, dy) / math.hypot(center_x, center_y)
                
                if dist_ratio > 0.7:  # Only affect edges
                    # Subtle character shifting for chromatic effect
                    shift = int(dist_ratio * 2)
                    if x + shift < width and screen[y][x + shift] != ' ':
                        aberrated[y][x] = screen[y][x + shift]
        
        return [''.join(row) for row in aberrated]

    def render_volumetric_lighting(self, screen: List[str], width: int, height: int, world_map: List[str]) -> List[str]:
        """Render volumetric lighting rays"""
        if not self.gi_volumetrics:
            return screen
        
        horizon_y = height // 2
        
        # Render light rays from sources
        for lx, ly, light_char in self.light_sources:
            # Cast rays in multiple directions
            for angle in [0, math.pi/4, math.pi/2, 3*math.pi/4, math.pi, 5*math.pi/4, 3*math.pi/2, 7*math.pi/4]:
                ray_x = lx
                ray_y = ly
                dx = math.cos(angle) * 0.5
                dy = math.sin(angle) * 0.5
                intensity = 1.0
                
                for step in range(int(self.light_radius * 2)):
                    ray_x += dx
                    ray_y += dy
                    
                    # Check bounds
                    if not (0 <= int(ray_x) < len(world_map[0]) and 0 <= int(ray_y) < len(world_map)):
                        break
                    
                    # Hit wall - stop ray
                    if world_map[int(ray_y)][int(ray_x)] not in {'.', '·', '~', ' '}:
                        break
                    
                    # Add volumetric effect to screen
                    screen_x = int(ray_x * width / len(world_map[0]))
                    screen_y = int(ray_y * height / len(world_map))
                    
                    if 0 <= screen_x < width and 0 <= screen_y < height:
                        current = screen[screen_y][screen_x]
                        if current in ' ·`':
                            # Add subtle ray visibility
                            if random.random() < intensity * 0.1:
                                line = screen[screen_y]
                                screen[screen_y] = line[:screen_x] + '·' + line[screen_x + 1:]
                    
                    intensity *= 0.8
                    if intensity < 0.1:
                        break
        
        return screen

    def apply_motion_blur(self, screen: List[str], player_velocity: float) -> List[str]:
        """Apply motion blur based on movement speed"""
        if not self.motion_blur or player_velocity < 0.1:
            return screen
        
        blur_amount = min(3, int(player_velocity * 10))
        blurred = [list(row) for row in screen]
        
        # Horizontal blur based on movement
        for y in range(len(screen)):
            for x in range(len(screen[0]) - blur_amount):
                if screen[y][x] != ' ':
                    for offset in range(1, blur_amount + 1):
                        if x + offset < len(screen[0]) and blurred[y][x + offset] == ' ':
                            blurred[y][x + offset] = '░'
        
        return [''.join(row) for row in blurred]

    def apply_depth_of_field(self, screen: List[str], focus_distance: float) -> List[str]:
        """Apply depth of field blur"""
        if not self.dof:
            return screen
        
        height = len(screen)
        width = len(screen[0]) if screen else 0
        center_y = height // 2
        
        blurred = [list(row) for row in screen]
        
        for y in range(height):
            # Calculate depth based on vertical position
            depth = abs(y - center_y) / max(1, center_y)
            blur_intensity = abs(depth - focus_distance / 10.0)
            
            if blur_intensity > 0.3:
                # Simple blur by character substitution
                for x in range(width):
                    current = screen[y][x]
                    if current in '█▓▒':
                        blurred[y][x] = '▒'
                    elif current in '▒░':
                        blurred[y][x] = '░'
        
        return [''.join(row) for row in blurred]

    def render_enhanced_sky(self, screen: List[str], width: int, sky_height: int, theme: str = 'quantum') -> List[str]:
        """Render next-gen animated sky with advanced effects"""
        if not self.sky_animated:
            return screen
            
        # Enhanced theme-specific sky
        sky_themes = {
            'quantum': {
                'stars': ['·', '∘', '○', '◯', '*', '★'], 
                'nebula': ['▫', '▪', '◦', '●'],
                'base': ' '
            },
            'atman': {
                'stars': ['·', '°', '˚', '∙', '•', '●'],
                'nebula': ['░', '▒', '▓', '█'],
                'base': ' '
            },
            'loqiemean': {
                'stars': ['~', '≈', '∿', '〜', '⩙'],
                'nebula': ['▱', '▰', '◪', '◫'],
                'base': ' '
            },
            'batut': {
                'stars': ['`', '´', '¨', '¸', '˜'],
                'nebula': ['⚬', '⚭', '⚮', '⚯'],
                'base': ' '
            }
        }
        
        sky_data = sky_themes.get(theme, sky_themes['quantum'])
        stars = sky_data['stars']
        nebula = sky_data['nebula']
        
        for y in range(sky_height):
            line = ''
            for x in range(width):
                # Multi-layered procedural sky
                star_seed = (x * 17 + y * 23 + self.tick // 12) % 1000
                nebula_seed = (x * 11 + y * 19 + self.tick // 20) % 1000
                
                # Star layer with advanced twinkling
                if star_seed < 8:  # 0.8% star density
                    twinkle_phase = (star_seed + self.tick // 3) % len(stars)
                    intensity = math.sin(star_seed * 0.1 + self.tick * 0.05) * 0.5 + 0.5
                    star_idx = int(intensity * (len(stars) - 1))
                    line += stars[star_idx]
                # Nebula layer
                elif nebula_seed < 15 and y > sky_height // 4:
                    nebula_phase = math.sin((x * 0.05 + self.tick * 0.02)) * 0.3 + 0.7
                    nebula_idx = int(nebula_phase * (len(nebula) - 1))
                    line += nebula[nebula_idx]
                # Atmospheric layers
                elif y > sky_height * 0.8:
                    # Lower atmosphere
                    atmo_intensity = math.sin((x * 0.08 + self.tick * self.fog_speed * 0.03)) * 0.4
                    line += '░' if atmo_intensity > 0.2 else sky_data['base']
                else:
                    line += sky_data['base']
            screen[y] = line
        
        return screen

    def spawn_blood(self, x: float, y: float, amount: int = 5):
        """Spawn blood particles and fluid"""
        if not self.particles_enabled:
            return
        
        # Blood particles
        for _ in range(amount):
            dx = random.uniform(-0.3, 0.3)
            dy = random.uniform(-0.2, 0.1)
            self.particles.append(Particle(x, y, dx, dy, '●', self.debris_ttl, 'blood'))
        
        # Blood fluid on ground
        if self.fluids_enabled:
            fx, fy = int(x), int(y)
            self.fluids[(fx, fy)] = FluidCell(fx, fy, 'blood')

    def damage_wall(self, x: int, y: int, damage: int = 1):
        """Damage wall at position"""
        if not self.destructibles:
            return
        
        pos = (x, y)
        current_damage = self.damaged_walls.get(pos, 0)
        self.damaged_walls[pos] = min(5, current_damage + damage)
        
        # Spawn debris particles
        debris_count = damage * 2
        for _ in range(debris_count):
            dx = random.uniform(-0.3, 0.3)
            dy = random.uniform(-0.1, 0.3)
            debris_char = random.choice(['.', ',', '`', '˙', '¸'])
            self.particles.append(Particle(x + 0.5, y + 0.5, dx, dy, debris_char, self.debris_ttl, 'debris'))

    def get_damaged_wall_char(self, x: int, y: int, original_char: str) -> str:
        """Get wall character with damage applied"""
        if not self.destructibles:
            return original_char
        
        damage = self.damaged_walls.get((x, y), 0)
        if damage == 0:
            return original_char
        
        # Progressive damage visualization
        damage_chars = {
            1: {'█': '▓', '▓': '▒', '▒': '░'},
            2: {'█': '▒', '▓': '░', '▒': '·'},
            3: {'█': '░', '▓': '·', '▒': '`'},
            4: {'█': '·', '▓': '`', '▒': ' '},
            5: {'█': ' ', '▓': ' ', '▒': ' '}  # Destroyed
        }
        
        char_map = damage_chars.get(damage, {})
        return char_map.get(original_char, original_char)

    def calculate_reflection(self, screen_x: int, screen_y: int, world_map: List[str], player_x: float, player_y: float, player_angle: float) -> str:
        """Calculate reflection for glossy surfaces"""
        if not self.reflections:
            return ' '
        
        # Simple reflection approximation
        # Cast ray in mirror direction
        mirror_angle = player_angle + math.pi
        rx = player_x + math.cos(mirror_angle) * 2.0
        ry = player_y + math.sin(mirror_angle) * 2.0
        
        # Check if reflection point is valid
        if 0 <= int(ry) < len(world_map) and 0 <= int(rx) < len(world_map[0]):
            reflected_char = world_map[int(ry)][int(rx)]
            if reflected_char not in {'.', '·', '~', ' '}:
                return '░'  # Dim reflection
        
        return ' '

    def render_particles_3d(self, screen: List[str], player_x: float, player_y: float, player_angle: float, fov: float, width: int) -> List[str]:
        """Enhanced 3D particle rendering"""
        if not self.particles_enabled:
            return screen
            
        horizon_y = len(screen) // 2
        
        for particle in self.particles:
            # Convert world position to screen position
            dx = particle.x - player_x
            dy = particle.y - player_y
            dist = math.hypot(dx, dy)
            
            if dist < 0.1:
                continue
                
            # Check FOV
            angle_to_particle = math.atan2(dy, dx) - player_angle
            angle_to_particle = (angle_to_particle + math.pi) % (2 * math.pi) - math.pi
            
            if abs(angle_to_particle) < fov / 2:
                # Enhanced perspective calculation
                sx = int((angle_to_particle + fov / 2) / fov * width)
                
                # Perspective height with particle type consideration
                if particle.type == 'smoke':
                    sy = max(0, horizon_y - int(15 / max(dist, 0.1)))
                elif particle.type == 'spark':
                    sy = horizon_y + random.randint(-2, 2)  # Jittery sparks
                else:
                    sy = horizon_y + int(8 / max(dist, 0.1))
                
                if 0 <= sx < width and 0 <= sy < len(screen):
                    char = particle.get_char()
                    
                    # Glow effect for certain particles
                    if particle.glow:
                        # Enhance surrounding area
                        for dy in [-1, 0, 1]:
                            for dx in [-1, 0, 1]:
                                nx, ny = sx + dx, sy + dy
                                if 0 <= nx < width and 0 <= ny < len(screen):
                                    if dx == 0 and dy == 0:
                                        continue
                                    current = screen[ny][nx]
                                    if current == ' ':
                                        line = screen[ny]
                                        screen[ny] = line[:nx] + '·' + line[nx + 1:]
                    
                    # Place main particle
                    line = screen[sy]
                    screen[sy] = line[:sx] + char + line[sx + 1:]
        
        return screen

    def render_fluid_layer(self, screen: List[str], world_map: List[str]) -> List[str]:
        """Render fluid effects on floor"""
        if not self.fluids_enabled:
            return screen
        
        height = len(screen)
        width = len(screen[0]) if screen else 0
        floor_y = height * 3 // 4  # Floor area
        
        for pos, fluid in self.fluids.items():
            fx, fy = pos
            # Convert world to screen coordinates (simplified)
            sx = fx * width // len(world_map[0]) if world_map else fx
            sy = fy * height // len(world_map) if world_map else fy
            
            if 0 <= sx < width and 0 <= sy < height and sy > height // 2:
                char = fluid.get_char()
                line = screen[sy]
                screen[sy] = line[:sx] + char + line[sx + 1:]
        
        return screen

    def spawn_sparks(self, x: float, y: float, count: int = 3):
        """Enhanced spark spawning with types"""
        if not self.particles_enabled or len(self.particles) > self.particles_max:
            return
            
        spark_chars = ['*', '+', '·', '✦', '✧', '✩']
        for _ in range(count):
            dx = random.uniform(-0.25, 0.25)
            dy = random.uniform(-0.25, 0.25)
            char = random.choice(spark_chars)
            self.particles.append(Particle(x, y, dx, dy, char, self.sparks_ttl, 'spark'))

    def spawn_debris(self, x: float, y: float, count: int = 8):
        """Enhanced debris with wall damage"""
        if not self.particles_enabled or len(self.particles) > self.particles_max:
            return
            
        # Damage nearby walls
        if self.destructibles:
            for dx in range(-1, 2):
                for dy in range(-1, 2):
                    self.damage_wall(int(x) + dx, int(y) + dy, 1)
        
        debris_chars = ['.', ',', '`', '¸', '˙', '‾', '_']
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(0.15, 0.5)
            dx = math.cos(angle) * speed
            dy = math.sin(angle) * speed
            char = random.choice(debris_chars)
            self.particles.append(Particle(x, y, dx, dy, char, self.debris_ttl, 'debris'))

    def spawn_smoke_trail(self, x: float, y: float):
        """Enhanced smoke trail"""
        if not self.particles_enabled or len(self.particles) > self.particles_max:
            return
            
        dx = random.uniform(-0.08, 0.08)
        dy = random.uniform(-0.08, 0.08)
        smoke_chars = ['○', '°', '∘', '◦']
        char = random.choice(smoke_chars)
        self.particles.append(Particle(x, y, dx, dy, char, 8, 'smoke'))

    def update_light_sources(self, world_map: List[str]):
        """Cache light source positions"""
        if not self.lights_enabled:
            self.light_sources = []
            return
            
        self.light_sources = []
        special_chars = {'Q', 'A', 'L', 'B'}
        
        for y, row in enumerate(world_map):
            for x, char in enumerate(row):
                if char in special_chars:
                    self.light_sources.append((x, y, char))

    def get_enhanced_light_intensity(self, x: int, y: int, world_map: List[str] = None) -> float:
        """Enhanced lighting with shadows and GI"""
        if not self.lights_enabled or not self.light_sources:
            return 1.0
            
        total_intensity = 0.8  # Slightly darker base
        
        for lx, ly, light_char in self.light_sources:
            dist = math.hypot(x - lx, y - ly)
            if dist <= self.light_radius:
                # Check shadows if enabled
                shadow_factor = 1.0
                if self.shadows and world_map:
                    shadow_factor = self._calculate_shadow(x, y, lx, ly, world_map)
                
                # Enhanced pulsing per light type
                pulse_patterns = {
                    'Q': lambda t: math.sin(t * 0.15) * 0.4 + 0.6,  # Steady quantum pulse
                    'A': lambda t: math.sin(t * 0.12 + math.pi/4) * 0.3 + 0.7,  # Warm atman glow
                    'L': lambda t: (math.sin(t * 0.18) * math.cos(t * 0.07)) * 0.5 + 0.5,  # Complex loqi wave
                    'B': lambda t: abs(math.sin(t * 0.1)) * 0.6 + 0.4  # Earth pulse
                }
                
                pulse_fn = pulse_patterns.get(light_char, pulse_patterns['Q'])
                pulse = pulse_fn(self.tick * self.light_pulse_speed * 0.1)
                
                base_intensity = max(0.1, 1.0 - dist / self.light_radius)
                light_contribution = base_intensity * pulse * shadow_factor
                total_intensity = min(2.5, total_intensity + light_contribution)
        
        return total_intensity
    
    def _calculate_shadow(self, x: int, y: int, lx: int, ly: int, world_map: List[str]) -> float:
        """Simple shadow calculation"""
        # Ray from light to point
        steps = max(abs(x - lx), abs(y - ly))
        if steps == 0:
            return 1.0
        
        dx = (x - lx) / steps
        dy = (y - ly) / steps
        
        shadow_intensity = 1.0
        for step in range(1, steps):
            rx = lx + dx * step
            ry = ly + dy * step
            mx, my = int(rx), int(ry)
            
            if 0 <= my < len(world_map) and 0 <= mx < len(world_map[0]):
                if world_map[my][mx] not in {'.', '·', '~', ' '}:
                    shadow_intensity *= 0.3  # Blocked by wall
        
        return shadow_intensity