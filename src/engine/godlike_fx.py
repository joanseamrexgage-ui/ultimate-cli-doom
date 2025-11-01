"""
🌌 GODLIKE ASCII GRAPHICS - Reality-bending visual effects
The ultimate evolution of CLI graphics technology
"""

import math
import random
from typing import List, Tuple, Dict, Set
from collections import deque

class QuantumEffect:
    def __init__(self, x: int, y: int, effect_type: str, duration: int):
        self.x = x
        self.y = y
        self.type = effect_type  # 'hologram', 'glitch', 'tunnel', 'matrix'
        self.duration = duration
        self.max_duration = duration
        self.phase = random.uniform(0, 2 * math.pi)
    
    def update(self):
        self.duration -= 1
        self.phase += 0.2
    
    def is_active(self) -> bool:
        return self.duration > 0
    
    def get_effect_char(self, base_char: str) -> str:
        intensity = self.duration / self.max_duration
        
        if self.type == 'hologram':
            # Flicker between reality states
            flicker = math.sin(self.phase * 3) * 0.5 + 0.5
            if flicker < 0.3:
                return ' '  # Disappear
            elif flicker < 0.6:
                return '░'  # Translucent
            else:
                return base_char
        
        elif self.type == 'glitch':
            # Reality distortion
            glitch_chars = ['▓', '▒', '░', '█', '▄', '▀', '▌', '▐']
            return random.choice(glitch_chars)
        
        elif self.type == 'tunnel':
            # Quantum tunneling transparency
            tunnel_chars = [base_char, '▒', '░', '·', ' ']
            idx = int((1 - intensity) * (len(tunnel_chars) - 1))
            return tunnel_chars[idx]
        
        elif self.type == 'matrix':
            # Matrix rain effect
            matrix_chars = ['0', '1', '２', '３', '４', '５', '６', '７', '８', '９']
            return random.choice(matrix_chars)
        
        return base_char

class LivingWall:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
        self.breath_phase = random.uniform(0, 2 * math.pi)
        self.growth_level = 0.0
        self.pulsation_speed = random.uniform(0.05, 0.15)
    
    def update(self):
        self.breath_phase += self.pulsation_speed
        self.growth_level = min(1.0, self.growth_level + 0.01)
    
    def get_breathing_char(self, base_char: str, biome: str) -> str:
        breath = math.sin(self.breath_phase) * 0.5 + 0.5
        
        if biome == 'quantum':
            # Crystal growth
            if self.growth_level > 0.8 and breath > 0.7:
                return '◆'
            elif breath > 0.5:
                return '♦'
            else:
                return base_char
        
        elif biome == 'atman':
            # Organic spreading
            organic_chars = ['♠', '♣', '♥', '♦', '❀', '✿']
            if self.growth_level > 0.6 and breath > 0.6:
                return random.choice(organic_chars)
            else:
                return base_char
        
        elif biome == 'loqiemean':
            # Coral growth
            coral_chars = ['≈', '∿', '〰', '∾']
            if breath > 0.8:
                return random.choice(coral_chars)
            else:
                return base_char
        
        elif biome == 'batut':
            # Root systems
            root_chars = ['┤', '├', '┬', '┴', '┼']
            if self.growth_level > 0.5 and breath > 0.7:
                return random.choice(root_chars)
            else:
                return base_char
        
        return base_char

class GodlikeGraphicsFX:
    def __init__(self, config: Dict):
        self.config = config.get('graphics', {})
        self.godlike_config = config.get('godlike_fx', {})
        
        self.tick = 0
        self.quantum_effects = []
        self.living_walls = {}
        self.player_ghosts = deque(maxlen=10)  # Trail of previous positions
        self.time_dilation = 1.0
        self.emotion_state = 'normal'  # 'critical', 'rage', 'calm'
        
        # Godlike feature flags
        self.hologram_projection = bool(self.godlike_config.get('hologram_projection', False))
        self.matrix_rain = bool(self.godlike_config.get('matrix_rain', False))
        self.quantum_tunneling = bool(self.godlike_config.get('quantum_tunneling', False))
        self.reality_glitch = bool(self.godlike_config.get('reality_glitch', False))
        self.living_walls = bool(self.godlike_config.get('living_walls', False))
        self.growing_crystals = bool(self.godlike_config.get('growing_crystals', False))
        self.ai_upscaling = bool(self.godlike_config.get('ai_upscaling', False))
        self.emotion_driven = bool(self.godlike_config.get('emotion_driven', False))
        self.electromagnetic_fields = bool(self.godlike_config.get('electromagnetic_fields', False))
        self.time_effects = bool(self.godlike_config.get('time_effects', False))
        self.portal_rendering = bool(self.godlike_config.get('portal_rendering', False))
        self.thermal_imaging = bool(self.godlike_config.get('thermal_imaging', False))
        
        # Effect intensities
        self.glitch_intensity = float(self.godlike_config.get('glitch_intensity', 0.1))
        self.hologram_flicker = float(self.godlike_config.get('hologram_flicker', 0.3))
        self.wall_breathing = float(self.godlike_config.get('wall_breathing', 0.2))
        
        # Living wall cache
        self.wall_entities = {}

    def update(self, player_health: int = 100, player_velocity: float = 0.0):
        """Update all godlike effects"""
        self.tick += 1
        
        # Update emotion state
        if self.emotion_driven:
            if player_health < 20:
                self.emotion_state = 'critical'
            elif player_velocity > 0.3:
                self.emotion_state = 'rage'
            else:
                self.emotion_state = 'normal'
        
        # Update time dilation
        if self.time_effects and player_health < 30:
            self.time_dilation = max(0.3, 0.5 + player_health * 0.01)
        else:
            self.time_dilation = 1.0
        
        # Update quantum effects
        self.quantum_effects = [e for e in self.quantum_effects if e.is_active()]
        for effect in self.quantum_effects:
            effect.update()
        
        # Update living walls
        if self.living_walls:
            for wall in self.wall_entities.values():
                wall.update()

    def spawn_hologram_projection(self, x: int, y: int, duration: int = 60):
        """Spawn holographic flickering effect"""
        if not self.hologram_projection:
            return
        self.quantum_effects.append(QuantumEffect(x, y, 'hologram', duration))

    def spawn_matrix_rain(self, screen_width: int, intensity: int = 20):
        """Spawn matrix rain effects"""
        if not self.matrix_rain:
            return
        
        for _ in range(intensity):
            x = random.randint(0, screen_width - 1)
            y = random.randint(0, 10)  # Top area
            self.quantum_effects.append(QuantumEffect(x, y, 'matrix', 40))

    def spawn_reality_glitch(self, x: int, y: int, radius: int = 3):
        """Spawn reality distortion glitch"""
        if not self.reality_glitch:
            return
        
        for dx in range(-radius, radius + 1):
            for dy in range(-radius, radius + 1):
                if random.random() < self.glitch_intensity:
                    self.quantum_effects.append(QuantumEffect(x + dx, y + dy, 'glitch', 15))

    def enable_quantum_tunneling(self, enemy_x: int, enemy_y: int):
        """Make enemy translucent during teleportation"""
        if not self.quantum_tunneling:
            return
        self.quantum_effects.append(QuantumEffect(enemy_x, enemy_y, 'tunnel', 30))

    def initialize_living_walls(self, world_map: List[str]):
        """Initialize breathing wall system"""
        if not self.living_walls:
            return
        
        self.wall_entities = {}
        for y, row in enumerate(world_map):
            for x, char in enumerate(row):
                if char not in {'.', '·', '~', ' '}:  # Wall characters
                    if random.random() < 0.1:  # 10% of walls are alive
                        self.wall_entities[(x, y)] = LivingWall(x, y)

    def get_emotion_palette(self, base_palette: List[str]) -> List[str]:
        """Get emotion-driven color palette"""
        if not self.emotion_driven:
            return base_palette
        
        emotion_palettes = {
            'critical': [' ', '▓', '█', '▉', '▊'],  # Darker, more intense
            'rage': [' ', '▒', '▓', '█', '█'],      # High contrast
            'normal': base_palette,
            'calm': [' ', '░', '▒', '▓', '█']       # Softer gradients
        }
        
        return emotion_palettes.get(self.emotion_state, base_palette)

    def apply_ai_upscaling(self, screen: List[str]) -> List[str]:
        """Apply AI-like character enhancement"""
        if not self.ai_upscaling:
            return screen
        
        enhanced = []
        for y, row in enumerate(screen):
            enhanced_row = ""
            for x, char in enumerate(row):
                # AI enhancement based on surrounding context
                context = self._get_local_context(screen, x, y)
                enhanced_char = self._ai_enhance_char(char, context, x, y)
                enhanced_row += enhanced_char
            enhanced.append(enhanced_row)
        
        return enhanced

    def _get_local_context(self, screen: List[str], x: int, y: int) -> str:
        """Get 3x3 context around character"""
        context = ""
        for dy in range(-1, 2):
            for dx in range(-1, 2):
                nx, ny = x + dx, y + dy
                if 0 <= nx < len(screen[0]) and 0 <= ny < len(screen):
                    context += screen[ny][nx]
                else:
                    context += " "
        return context

    def _ai_enhance_char(self, char: str, context: str, x: int, y: int) -> str:
        """AI-driven character enhancement"""
        # Count similar characters in context
        char_density = context.count(char)
        
        # Enhancement based on local patterns
        if char in '█▓▒░':
            # Wall enhancement
            if char_density >= 6:  # Surrounded by similar
                enhancement_map = {
                    '░': '▒',
                    '▒': '▓', 
                    '▓': '█',
                    '█': '██'[random.randint(0, 1)]  # Occasional double
                }
                return enhancement_map.get(char, char)
        
        elif char in '·•∙':
            # Particle enhancement
            noise = (x * 7 + y * 11 + self.tick) % 100
            if noise < 5:  # 5% enhancement chance
                return '★' if char == '·' else '✦'
        
        return char

    def apply_thermal_imaging(self, screen: List[str], enemies: List) -> List[str]:
        """Apply thermal imaging effect"""
        if not self.thermal_imaging:
            return screen
        
        thermal = [list(row) for row in screen]
        
        # Heat signatures for enemies
        for enemy in enemies:
            if not getattr(enemy, 'alive', False):
                continue
            
            # Convert world to screen coordinates (simplified)
            ex, ey = int(enemy.x * len(screen[0]) / 50), int(enemy.y * len(screen) / 50)
            
            # Apply heat signature
            for dy in range(-2, 3):
                for dx in range(-2, 3):
                    nx, ny = ex + dx, ey + dy
                    if 0 <= nx < len(screen[0]) and 0 <= ny < len(screen):
                        distance = math.hypot(dx, dy)
                        if distance <= 2:
                            heat_intensity = 1.0 - distance / 2.0
                            if heat_intensity > 0.7:
                                thermal[ny][nx] = '◉'
                            elif heat_intensity > 0.4:
                                thermal[ny][nx] = '●'
                            elif heat_intensity > 0.2:
                                thermal[ny][nx] = '○'
        
        return [''.join(row) for row in thermal]

    def apply_time_dilation_effects(self, screen: List[str]) -> List[str]:
        """Apply time dilation visual effects"""
        if not self.time_effects or self.time_dilation >= 0.8:
            return screen
        
        # Time ripple effect
        dilated = [list(row) for row in screen]
        center_x, center_y = len(screen[0]) // 2, len(screen) // 2
        
        for y in range(len(screen)):
            for x in range(len(screen[0])):
                # Create time ripple distortion
                dist_from_center = math.hypot(x - center_x, y - center_y)
                ripple_phase = dist_from_center * 0.1 + self.tick * 0.05
                ripple = math.sin(ripple_phase) * (1 - self.time_dilation)
                
                if abs(ripple) > 0.3:
                    # Distort character based on time field
                    if ripple > 0:
                        dilated[y][x] = '◊'  # Time acceleration
                    else:
                        dilated[y][x] = '◈'  # Time deceleration
        
        return [''.join(row) for row in dilated]

    def render_portal_effects(self, screen: List[str], portal_x: int, portal_y: int, target_view: List[str] = None) -> List[str]:
        """Render portal showing other area"""
        if not self.portal_rendering or not target_view:
            return screen
        
        portal_radius = 4
        portal = [list(row) for row in screen]
        
        # Create portal aperture
        for dy in range(-portal_radius, portal_radius + 1):
            for dx in range(-portal_radius, portal_radius + 1):
                x, y = portal_x + dx, portal_y + dy
                if 0 <= x < len(screen[0]) and 0 <= y < len(screen):
                    distance = math.hypot(dx, dy)
                    if distance <= portal_radius:
                        # Portal rim
                        if distance > portal_radius - 1:
                            portal[y][x] = '◊'
                        # Portal interior - show target view
                        elif distance < portal_radius - 1 and target_view:
                            tx, ty = min(x, len(target_view[0]) - 1), min(y, len(target_view) - 1)
                            if tx >= 0 and ty >= 0:
                                portal_char = target_view[ty][tx]
                                # Add portal distortion
                                distortion = math.sin(distance * 0.5 + self.tick * 0.1)
                                if distortion > 0.3:
                                    portal[y][x] = '▒'
                                else:
                                    portal[y][x] = portal_char
        
        return [''.join(row) for row in portal]

    def apply_electromagnetic_effects(self, screen: List[str], metallic_objects: List[Tuple[int, int]]) -> List[str]:
        """Apply electromagnetic field visualization"""
        if not self.electromagnetic_fields:
            return screen
        
        em_screen = [list(row) for row in screen]
        
        for obj_x, obj_y in metallic_objects:
            # Generate electromagnetic field lines
            field_strength = 1.0
            for angle in [0, math.pi/4, math.pi/2, 3*math.pi/4, math.pi, 5*math.pi/4, 3*math.pi/2, 7*math.pi/4]:
                fx, fy = obj_x, obj_y
                dx, dy = math.cos(angle) * 0.7, math.sin(angle) * 0.7
                
                for step in range(8):
                    fx += dx
                    fy += dy
                    sx, sy = int(fx), int(fy)
                    
                    if 0 <= sx < len(screen[0]) and 0 <= sy < len(screen):
                        if screen[sy][sx] == ' ':
                            field_vis = math.sin(step * 0.5 + self.tick * 0.1) * field_strength
                            if field_vis > 0.5:
                                em_screen[sy][sx] = '∿'
                            elif field_vis > 0.0:
                                em_screen[sy][sx] = '~'
                    
                    field_strength *= 0.7
                    if field_strength < 0.1:
                        break
        
        return [''.join(row) for row in em_screen]

    def apply_sound_visualization(self, screen: List[str], sound_sources: List[Tuple[int, int, str]]) -> List[str]:
        """Visualize sound waves"""
        sound_screen = [list(row) for row in screen]
        
        for sx, sy, sound_type in sound_sources:
            # Sound wave ripples
            wave_chars = {
                'gunshot': ['◦', '○', '◎', '●'],
                'explosion': ['◇', '◈', '◉', '●'],
                'footstep': ['·', '∘', '○']
            }
            
            chars = wave_chars.get(sound_type, ['○'])
            max_radius = len(chars) * 2
            
            for radius in range(1, max_radius):
                wave_phase = (self.tick * 0.2 - radius * 0.3) % (2 * math.pi)
                if math.sin(wave_phase) > 0.7:  # Wave peak
                    char_idx = min(len(chars) - 1, radius // 2)
                    char = chars[char_idx]
                    
                    # Draw circle
                    for angle in range(0, 360, 45):
                        rad = math.radians(angle)
                        wx = sx + int(math.cos(rad) * radius)
                        wy = sy + int(math.sin(rad) * radius)
                        
                        if 0 <= wx < len(screen[0]) and 0 <= wy < len(screen):
                            if screen[wy][wx] == ' ':
                                sound_screen[wy][wx] = char
        
        return [''.join(row) for row in sound_screen]

    def apply_xray_vision(self, screen: List[str], world_map: List[str], show_enemies: bool = True) -> List[str]:
        """Apply X-ray vision through thin walls"""
        if not hasattr(self, 'xray_enabled') or not self.xray_enabled:
            return screen
        
        xray_screen = [list(row) for row in screen]
        
        # Make thin walls translucent
        for y in range(len(screen)):
            for x in range(len(screen[0])):
                if screen[y][x] in '▒░':  # Thin wall materials
                    # Check if there's something interesting behind
                    map_x = x * len(world_map[0]) // len(screen[0])
                    map_y = y * len(world_map) // len(screen)
                    
                    if 0 <= map_x < len(world_map[0]) and 0 <= map_y < len(world_map):
                        # Show hint of what's behind
                        xray_screen[y][x] = '┊'  # X-ray wall
        
        return [''.join(row) for row in xray_screen]

    def record_player_ghost(self, x: float, y: float):
        """Record player position for ghost trail"""
        self.player_ghosts.append((x, y, self.tick))

    def render_rewind_ghosts(self, screen: List[str], player_x: float, player_y: float) -> List[str]:
        """Render player movement trail"""
        if not self.time_effects or not self.player_ghosts:
            return screen
        
        ghost_screen = [list(row) for row in screen]
        
        for i, (gx, gy, ghost_tick) in enumerate(self.player_ghosts):
            age = self.tick - ghost_tick
            if age < 60:  # Show ghosts for 60 ticks
                # Convert to screen coordinates
                sx = int(gx * len(screen[0]) / 50)  # Assuming 50x50 world
                sy = int(gy * len(screen) / 50)
                
                if 0 <= sx < len(screen[0]) and 0 <= sy < len(screen):
                    # Fade ghost based on age
                    alpha = 1.0 - age / 60.0
                    if alpha > 0.7:
                        ghost_screen[sy][sx] = '▲'
                    elif alpha > 0.4:
                        ghost_screen[sy][sx] = '△'
                    elif alpha > 0.1:
                        ghost_screen[sy][sx] = '∵'
        
        return [''.join(row) for row in ghost_screen]

    def apply_living_wall_effects(self, screen: List[str], world_map: List[str], biome: str) -> List[str]:
        """Apply breathing wall animations"""
        if not self.living_walls:
            return screen
        
        living_screen = [list(row) for row in screen]
        
        for (wx, wy), wall in self.wall_entities.items():
            # Convert world to screen coordinates
            sx = wx * len(screen[0]) // len(world_map[0])
            sy = wy * len(screen) // len(world_map)
            
            if 0 <= sx < len(screen[0]) and 0 <= sy < len(screen):
                base_char = screen[sy][sx]
                breathing_char = wall.get_breathing_char(base_char, biome)
                living_screen[sy][sx] = breathing_char
        
        return [''.join(row) for row in living_screen]

    def apply_quantum_field_effects(self, screen: List[str]) -> List[str]:
        """Apply quantum field distortions"""
        quantum_screen = [list(row) for row in screen]
        
        for effect in self.quantum_effects:
            if 0 <= effect.x < len(screen[0]) and 0 <= effect.y < len(screen):
                base_char = screen[effect.y][effect.x]
                quantum_char = effect.get_effect_char(base_char)
                quantum_screen[effect.y][effect.x] = quantum_char
        
        return [''.join(row) for row in quantum_screen]

    def apply_procedural_detail_generation(self, screen: List[str], detail_level: float = 0.5) -> List[str]:
        """Generate procedural micro-details"""
        if not self.ai_upscaling:
            return screen
        
        detailed = [list(row) for row in screen]
        
        for y in range(len(screen)):
            for x in range(len(screen[0])):
                if screen[y][x] in '█▓▒':  # Wall surfaces
                    # Generate micro-detail based on position and time
                    detail_seed = (x * 13 + y * 17 + self.tick // 8) % 100
                    if detail_seed < detail_level * 10:
                        detail_chars = ['▪', '▫', '▬', '▭', '▮', '▯']
                        detail_idx = (detail_seed + x + y) % len(detail_chars)
                        detailed[y][x] = detail_chars[detail_idx]
        
        return [''.join(row) for row in detailed]

    def get_effect_multiplier(self) -> float:
        """Get time dilation multiplier for effects"""
        return self.time_dilation