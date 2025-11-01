"""
🎨 Advanced graphics effects system for atmospheric rendering
"""

import math
import random
from typing import List, Tuple, Dict

class Particle:
    def __init__(self, x: float, y: float, dx: float, dy: float, char: str, ttl: int):
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.char = char
        self.ttl = ttl
        self.max_ttl = ttl
        self.gravity = -0.02  # Slight downward drift
    
    def update(self):
        self.x += self.dx
        self.y += self.dy
        self.dy += self.gravity  # Apply gravity
        self.dx *= 0.98  # Air resistance
        self.ttl -= 1
    
    def is_alive(self) -> bool:
        return self.ttl > 0
    
    def get_char(self) -> str:
        # Fade particle over time
        fade_ratio = self.ttl / self.max_ttl
        if fade_ratio > 0.6:
            return self.char
        elif fade_ratio > 0.3:
            return '·'
        else:
            return '`'

class GraphicsFX:
    def __init__(self, config: Dict):
        self.config = config.get('graphics', {})
        self.tick = 0
        self.particles = []
        
        # Animation flags
        self.sky_animated = bool(self.config.get('sky_animated', False))
        self.fog_enabled = bool(self.config.get('fog_enabled', False))
        self.particles_enabled = bool(self.config.get('particles_enabled', False))
        self.lights_enabled = bool(self.config.get('lights_enabled', False))
        
        # Parameters
        self.fog_speed = float(self.config.get('fog_speed', 0.8))
        self.fog_intensity = float(self.config.get('fog_intensity', 0.25))
        self.sparks_ttl = int(self.config.get('sparks_ttl', 3))
        self.debris_ttl = int(self.config.get('debris_ttl', 8))
        self.particles_max = int(self.config.get('particles_max', 200))
        self.light_radius = float(self.config.get('light_radius', 3.0))
        self.light_pulse_speed = float(self.config.get('light_pulse_speed', 1.2))
        
        # Cache for light sources
        self.light_sources = []

    def update(self):
        """Update animation state"""
        self.tick += 1
        
        # Update particles
        if self.particles_enabled:
            self.particles = [p for p in self.particles if p.is_alive()]
            for p in self.particles:
                p.update()

    def render_animated_sky(self, screen: List[str], width: int, sky_height: int, theme: str = 'quantum'):
        """Render animated sky with stars and clouds"""
        if not self.sky_animated:
            return screen
            
        # Theme-specific sky characters
        sky_themes = {
            'quantum': ['·', '∘', '○', '◯', '*'],
            'atman': ['·', '°', '˚', '∙', '⋅'],
            'loqiemean': ['~', '≈', '⌐', '¬', '∿'],
            'batut': ['`', '´', '¨', '¸', '˜']
        }
        
        sky_chars = sky_themes.get(theme, sky_themes['quantum'])
        
        for y in range(sky_height):
            line = ''
            for x in range(width):
                # Deterministic star twinkling based on position and time
                star_seed = (x * 7 + y * 13 + self.tick // 8) % 100
                
                if star_seed < 3:  # 3% star density
                    # Twinkling animation
                    twinkle = (star_seed + self.tick // 4) % len(sky_chars)
                    line += sky_chars[twinkle]
                elif star_seed < 8 and y > sky_height // 3:  # Light fog
                    fog_phase = math.sin((x * 0.1 + self.tick * self.fog_speed * 0.05)) * self.fog_intensity
                    line += sky_chars[1] if fog_phase > 0.1 else sky_chars[0]
                else:
                    line += sky_chars[0]  # Base sky
            screen[y] = line
        
        return screen

    def render_fog_layer(self, screen: List[str], width: int, horizon_y: int):
        """Render atmospheric fog at horizon"""
        if not self.fog_enabled or horizon_y >= len(screen):
            return screen
            
        fog_line = ''
        for x in range(width):
            # Wave-based fog intensity
            wave1 = math.sin((x * 0.15 + self.tick * self.fog_speed * 0.03))
            wave2 = math.sin((x * 0.08 + self.tick * self.fog_speed * 0.02) + math.pi/3)
            intensity = (wave1 + wave2) * 0.5 * self.fog_intensity
            
            if intensity > 0.2:
                fog_line += '≈'
            elif intensity > 0.0:
                fog_line += '∿'
            elif intensity > -0.2:
                fog_line += '~'
            else:
                fog_line += ' '
        
        screen[horizon_y] = fog_line
        return screen

    def spawn_sparks(self, x: float, y: float, count: int = 3):
        """Spawn hit sparks at location"""
        if not self.particles_enabled or len(self.particles) > self.particles_max:
            return
            
        spark_chars = ['*', '+', '·', '∗', '✦']
        for _ in range(count):
            dx = random.uniform(-0.2, 0.2)
            dy = random.uniform(-0.2, 0.2)
            char = random.choice(spark_chars)
            self.particles.append(Particle(x, y, dx, dy, char, self.sparks_ttl))

    def spawn_debris(self, x: float, y: float, count: int = 8):
        """Spawn explosion debris"""
        if not self.particles_enabled or len(self.particles) > self.particles_max:
            return
            
        debris_chars = ['.', ',', '`', '¸', '˙']
        for _ in range(count):
            # Radial explosion pattern
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(0.1, 0.4)
            dx = math.cos(angle) * speed
            dy = math.sin(angle) * speed
            char = random.choice(debris_chars)
            self.particles.append(Particle(x, y, dx, dy, char, self.debris_ttl))

    def spawn_smoke_trail(self, x: float, y: float):
        """Spawn smoke trail particle"""
        if not self.particles_enabled or len(self.particles) > self.particles_max:
            return
            
        # Slight random drift
        dx = random.uniform(-0.05, 0.05)
        dy = random.uniform(-0.05, 0.05)
        self.particles.append(Particle(x, y, dx, dy, '°', 6))

    def update_light_sources(self, world_map: List[str]):
        """Cache light source positions for efficient rendering"""
        if not self.lights_enabled:
            self.light_sources = []
            return
            
        self.light_sources = []
        special_chars = {'Q', 'A', 'L', 'B'}
        
        for y, row in enumerate(world_map):
            for x, char in enumerate(row):
                if char in special_chars:
                    self.light_sources.append((x, y, char))

    def get_light_intensity(self, x: int, y: int) -> float:
        """Get lighting intensity at position"""
        if not self.lights_enabled or not self.light_sources:
            return 1.0
            
        total_intensity = 1.0
        
        for lx, ly, light_char in self.light_sources:
            dist = math.hypot(x - lx, y - ly)
            if dist <= self.light_radius:
                # Pulsing light based on type and time
                pulse_offset = hash(light_char) % 100 / 100.0  # Per-light phase
                pulse = math.sin(self.tick * self.light_pulse_speed * 0.1 + pulse_offset * 2 * math.pi)
                base_intensity = max(0.2, 1.0 - dist / self.light_radius)
                light_boost = base_intensity * (1.0 + pulse * 0.3)
                total_intensity = min(2.0, total_intensity + light_boost)
        
        return total_intensity

    def render_particles(self, screen: List[str], player_x: float, player_y: float, player_angle: float, fov: float, width: int) -> List[str]:
        """Render particles in 3D space"""
        if not self.particles_enabled:
            return screen
            
        horizon_y = len(screen) // 2
        
        for particle in self.particles:
            # Convert world position to screen position
            dx = particle.x - player_x
            dy = particle.y - player_y
            dist = math.hypot(dx, dy)
            
            if dist == 0:
                continue
                
            # Check if particle is in field of view
            angle_to_particle = math.atan2(dy, dx) - player_angle
            angle_to_particle = (angle_to_particle + math.pi) % (2 * math.pi) - math.pi
            
            if abs(angle_to_particle) < fov / 2:
                # Calculate screen position
                sx = int((angle_to_particle + fov / 2) / fov * width)
                sy = horizon_y + int(10 / max(dist, 0.1))  # Perspective height
                
                if 0 <= sx < width and 0 <= sy < len(screen):
                    line = screen[sy]
                    char = particle.get_char()
                    screen[sy] = line[:sx] + char + line[sx+1:]
        
        return screen

    def get_biome_palette(self, theme: str, base_palette: List[str]) -> List[str]:
        """Get theme-specific wall palette"""
        palettes = {
            'quantum': [' ', '░', '▒', '▓', '█'],  # Cool/tech
            'atman': [' ', '∙', '∘', '●', '█'],     # Warm/organic  
            'loqiemean': [' ', '~', '≈', '▓', '█'], # Aquatic
            'batut': [' ', '`', '·', '▒', '█']      # Earth/natural
        }
        
        return palettes.get(theme, base_palette)