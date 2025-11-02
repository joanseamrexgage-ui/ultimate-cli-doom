"""
ABSOLUTE ASCII GRAPHICS Renderer
Beyond transcendence: Multiverse, 5D hyperspatial, consciousness waves
"""

import math
import os
import random
from typing import List, Tuple
from ..core.player import Player
from ..core.world import World
from .graphics_fx import NextGenGraphicsFX
from .godlike_fx import GodlikeGraphicsFX
from .transcendent_fx import TranscendentGraphicsFX
from .absolute_graphics import AbsoluteGraphicsEngine

try:
    import tomllib as toml
except Exception:
    toml = None

WALKABLE = {'.', '·', '~', ' '}

# ABSOLUTE wall material mappings with hyperdimensional properties
ABSOLUTE_MATERIALS = {
    'stone': {
        'symbols': ['▒', '▓', '█'], 
        'base': '▒',
        'dimensional_phase': 0.0,
        'consciousness_resonance': 0.1,
        'dna_compatibility': 0.3,
        'neural_conductivity': 0.0
    },
    'quantum_crystal': {
        'symbols': ['◆', '◇', '◈', '◉', '◊'], 
        'base': '◆',
        'dimensional_phase': 1.0,
        'consciousness_resonance': 1.0,
        'dna_compatibility': 0.8,
        'neural_conductivity': 0.9
    },
    'living_tissue': {
        'symbols': ['♥', '♡', '❤', '§', '♀'], 
        'base': '♥',
        'dimensional_phase': 0.5,
        'consciousness_resonance': 0.9,
        'dna_compatibility': 1.0,
        'neural_conductivity': 1.0
    },
    'void_matter': {
        'symbols': ['∅', '○', '◯', '◦', ' '], 
        'base': '∅',
        'dimensional_phase': -1.0,
        'consciousness_resonance': 0.0,
        'dna_compatibility': 0.0,
        'neural_conductivity': -0.5
    }
}

class AbsoluteRaycastingEngine:
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
        self.weapon_overlay_enabled = bool(g.get('weapon_overlay', False))  # Pacifist default
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
        
        # Initialize ALL graphics systems
        self.gfx = NextGenGraphicsFX(self.cfg)
        self.godlike = GodlikeGraphicsFX(self.cfg)
        self.transcendent = TranscendentGraphicsFX(self.cfg)
        self.absolute = AbsoluteGraphicsEngine(self.cfg)
        
        # Enhanced tracking
        self.visited = set()
        self.player_velocity = 0.0
        self.last_player_pos = (0.0, 0.0)
        self.sound_events = []  # For synesthesia
        self.critical_effects_active = False
        self.meditation_time = 0.0
        self.player_actions = []
        self.observer_angle_history = deque(maxlen=10)
        
        self.player = Player(x=1.5, y=1.5, angle=0)
        self.shake_ttl = 0
        self.muzzle_flash_ttl = 0
        self.projectiles = []
        self.banner_cb = None
        self.flash_cb = None
        self.damage_direction_cb = None

    def update_consciousness_state(self, action: str = None):
        """Track player consciousness for transcendent effects"""
        # Record actions for consciousness analysis
        if action:
            self.player_actions.append(action)
            if len(self.player_actions) > 10:
                self.player_actions.pop(0)
        
        # Track meditation time (stationary = meditation)
        if self.player_velocity < 0.01:
            self.meditation_time += 1/60.0  # Assuming 60 FPS
        else:
            self.meditation_time = max(0, self.meditation_time - 0.05)
        
        # Record viewing angles for observer effect
        self.observer_angle_history.append([int(self.player.angle * 180 / math.pi) % 360])

    def render_3d_absolute(self, world: World, enemies: List = None) -> List[str]:
        """ABSOLUTE rendering pipeline - the ultimate evolution"""
        if enemies is None:
            enemies = []  # Pacifist mode - no enemies
        
        # Update consciousness tracking
        self.update_consciousness_state()
        
        # Update player state tracking  
        current_pos = (self.player.x, self.player.y)
        self.player_velocity = math.hypot(
            current_pos[0] - self.last_player_pos[0],
            current_pos[1] - self.last_player_pos[1]
        )
        self.last_player_pos = current_pos
        
        # Update critical state
        self.critical_effects_active = self.player.health < 30
        
        if self.shake_ttl > 0:
            self.shake_ttl -= 1
        if self.muzzle_flash_ttl > 0:
            self.muzzle_flash_ttl -= 1

        # Update ALL graphics systems in hierarchy
        self.gfx.update()
        self.godlike.update(self.player.health, self.player_velocity)
        self.transcendent.update(self.player.health, self.player_actions, self.meditation_time)
        
        # Prepare absolute state
        absolute_player_state = {
            'x': self.player.x, 'y': self.player.y, 'health': self.player.health,
            'velocity': self.player_velocity, 'actions': self.player_actions,
            'stress': max(0, 1.0 - self.player.health / 100.0),
            'karma': self.transcendent.karma_score
        }
        self.absolute.update(absolute_player_state)
        
        self.gfx.update_light_sources(world.map)
        self.godlike.initialize_living_walls(world.map)
        self.transcendent.initialize_fractal_architecture(world.map)

        # Initialize screen
        screen = [' ' * self.width for _ in range(self.height)]
        sky_height = self.height // 2
        
        # ABSOLUTE RENDER PIPELINE:
        
        # 1. Cosmological background
        theme = getattr(world, 'theme', 'quantum')
        screen = self.gfx.render_enhanced_sky(screen, self.width, sky_height, theme)
        
        # 2. Volumetric lighting with consciousness fields
        screen = self.gfx.render_volumetric_lighting(screen, self.width, self.height, world.map)

        # 3. ABSOLUTE floor rendering with DNA evolution
        for y in range(self.height // 2, self.height):
            floor_line = ''
            floor_chars = [self.floor_char]
            
            # Theme-specific evolutionary floors
            if hasattr(world, 'theme'):
                evolved_floors = {
                    'quantum': ['.', '·', '¨', '⋅', '◆', '✦', '✪', '✫'],
                    'atman': ['·', '∘', '°', '◦', '♥', '♡', '❤', '♀'],     
                    'loqiemean': ['~', '≈', '∼', '〜', '○', '◯', '◎', '⦵'],
                    'batut': [' ', '·', '`', '‵', '┤', '│', '┊', '╍']
                }
                floor_chars = evolved_floors.get(world.theme, [self.floor_char])
            
            for x in range(self.width):
                # DNA-based procedural generation
                base_chance = 0.15  # Increased for richer environments
                
                # Evolutionary floor with genetic selection
                if self.absolute.dna_generation and self.absolute.ascii_genome:
                    # Use genetic algorithm for floor patterns
                    genome_factor = len([g for g in self.absolute.ascii_genome if g.fitness > 1.0])
                    if genome_factor > 5 and random.random() < 0.1:
                        best_gene = max(self.absolute.ascii_genome, key=lambda g: g.fitness)
                        env_factors = {'stress': 0.0, 'karma': self.transcendent.karma_score / 100.0}
                        evolved_char = best_gene.express(env_factors)
                        floor_line += evolved_char
                        continue
                
                # Neural network influence on floor
                if (self.absolute.neural_networks and 
                    (x // 5, y // 5) in self.absolute.neural_network):
                    neuron = self.absolute.neural_network[(x // 5 * 5, y // 5 * 5)]
                    if neuron.activation > 0.5:
                        floor_line += neuron.get_visual_state()
                        continue
                
                # Standard enhanced procedural with SSAO
                ssao_factor = self.gfx.calculate_ssao(screen, x, y)
                variation_chance = base_chance * ssao_factor
                
                if random.random() < variation_chance:
                    floor_line += random.choice(floor_chars)
                else:
                    floor_line += floor_chars[0]
            screen[y] = floor_line
        
        # Apply fluid layer
        screen = self.gfx.render_fluid_layer(screen, world.map)

        # 4. ABSOLUTE WALL RENDERING with all effects
        for col in range(self.width):
            sc = self._apply_shake(col)
            ray_angle = (self.player.angle - self.fov / 2 + col / self.width * self.fov)
            distance, wall_type, hit_x, hit_y, surface_normal = self.cast_ray_absolute(ray_angle, world.map)
            cd = self.correct_fish_eye(distance, ray_angle)
            wall_height = self.height if cd <= 0.1 else min(self.height, int(self.height / cd))
            
            # ABSOLUTE material character with all enhancements
            ch = self._get_absolute_material_char(wall_type, cd, world, hit_x, hit_y, surface_normal)
            
            y0 = max(0, self.height // 2 - wall_height // 2)
            y1 = min(self.height, self.height // 2 + wall_height // 2)
            
            for row in range(y0, y1):
                line = screen[row]
                
                # ABSOLUTE SSAO with all effects
                ssao_factor = self.gfx.calculate_ssao(screen, sc, row)
                
                # Reality distortions
                if self.godlike.reality_glitch and random.random() < 0.01:
                    ssao_factor *= random.uniform(0.5, 1.5)
                
                # Consciousness wave interference
                if self.transcendent.consciousness_state.value != 'normal':
                    consciousness_factor = math.sin(sc * 0.1 + row * 0.1 + self.transcendent.tick * 0.05)
                    ssao_factor *= (1.0 + consciousness_factor * 0.2)
                
                if ssao_factor < 0.7:
                    if ch == '█': ch = '▓'
                    elif ch == '▓': ch = '▒'
                    elif ch == '▒': ch = '░'
                
                screen[row] = line[:sc] + ch + line[sc+1:]

        # 5. Enhanced pickup rendering (no enemies in pacifist mode)
        screen = self._render_absolute_objects(screen, world, [])
        
        # 6. Advanced particle systems with all enhancements
        screen = self.gfx.render_particles_3d(screen, self.player.x, self.player.y, self.player.angle, self.fov, self.width)

        # 7. ULTIMATE POST-PROCESSING PIPELINE:
        
        # Layer 1: GODLIKE effects
        screen = self.godlike.apply_living_wall_effects(screen, world.map, theme)
        screen = self.godlike.apply_quantum_field_effects(screen)
        
        # Layer 2: TRANSCENDENT effects
        screen = self.transcendent.apply_psychedelic_distortion(screen)
        screen = self.transcendent.apply_non_euclidean_geometry(screen, self.player.x, self.player.y)
        screen = self.transcendent.apply_observer_effect(screen, self.player.angle, list(self.observer_angle_history))
        screen = self.transcendent.render_chakra_aura(screen, int(self.player.x), int(self.player.y), 
            {'heart': 1.0, 'crown': self.transcendent.enlightenment_progress})
        screen = self.transcendent.apply_schrodinger_rendering(screen, [])
        
        # Convert sound events for synesthesia
        synesthesia_sounds = [(int(self.player.x), int(self.player.y), 'ambient', 0.5)]
        if self.sound_events:
            for sx, sy, sound_type in self.sound_events:
                synesthesia_sounds.append((sx, sy, sound_type, 1.0))
        
        screen = self.transcendent.apply_synesthesia_sound_waves(screen, synesthesia_sounds)
        screen = self.transcendent.render_sacred_geometry(screen)
        screen = self.transcendent.render_astral_projection(screen)
        screen = self.transcendent.apply_karma_visualization(screen)
        screen = self.transcendent.apply_dream_logic_rendering(screen, world.map)
        screen = self.transcendent.render_divine_illumination(screen)
        
        # Layer 3: ABSOLUTE effects (ultimate layer)
        screen = self.absolute.render_absolute_effects(screen, absolute_player_state)
        
        # Clear sound events after processing
        self.sound_events.clear()
        
        # Layer 4: Standard post-processing (protected)
        screen = self.gfx.apply_bloom(screen)
        screen = self.gfx.apply_motion_blur(screen, self.player_velocity)
        screen = self.gfx.apply_depth_of_field(screen, self.gfx.dof_focus)
        screen = self.gfx.apply_chromatic_aberration(screen)

        # 8. Protected UI overlays
        screen = self._render_absolute_minimap(screen, world, [])

        if self.weapon_overlay_enabled:
            self._overlay_meditation_interface(screen)  # Pacifist mode interface
            
        return screen

    def _get_absolute_material_char(self, wall_type: str, distance: float, world: World, hit_x: int, hit_y: int, angle: float) -> str:
        """ABSOLUTE material rendering with all dimensional effects"""
        if not self.materials_enabled:
            return self._shade(distance)
            
        # Determine material with absolute enhancements
        material = getattr(world, 'material', 'stone')
        if hasattr(world, 'theme'):
            absolute_material_map = {
                'quantum': 'quantum_crystal',
                'atman': 'living_tissue',  # Evolved!
                'loqiemean': 'stone',
                'batut': 'living_tissue',
                'void': 'void_matter'  # New!
            }
            material = absolute_material_map.get(world.theme, 'stone')
        
        if distance >= self.max_depth:
            return ' '
            
        mat_data = ABSOLUTE_MATERIALS.get(material, ABSOLUTE_MATERIALS['stone'])
        symbols = mat_data['symbols']
        
        # ABSOLUTE SHADER PIPELINE:
        
        # 1. Base distance with hyperdimensional correction
        t = min(0.99, distance / self.max_depth)
        
        # 2. Consciousness resonance
        if mat_data['consciousness_resonance'] > 0:
            consciousness_wave = math.sin(self.transcendent.tick * 0.1 + hit_x * 0.2)
            consciousness_factor = consciousness_wave * mat_data['consciousness_resonance']
            t = max(0, t - consciousness_factor * 0.2)
        
        # 3. DNA compatibility effects
        if mat_data['dna_compatibility'] > 0 and self.absolute.ascii_genome:
            # Walls can be infected by genetic patterns
            avg_fitness = sum(g.fitness for g in self.absolute.ascii_genome) / len(self.absolute.ascii_genome)
            if avg_fitness > 1.2:
                genetic_influence = (avg_fitness - 1.0) * mat_data['dna_compatibility']
                t = max(0, t - genetic_influence * 0.1)
        
        # 4. Neural conductivity
        if mat_data['neural_conductivity'] != 0:
            # Check nearby neural activity
            nearby_neurons = [
                neuron for pos, neuron in self.absolute.neural_network.items()
                if abs(pos[0] - hit_x * 80 // len(world.map[0])) < 10 and 
                   abs(pos[1] - hit_y * 50 // len(world.map)) < 10
            ]
            
            if nearby_neurons:
                avg_activation = sum(n.activation for n in nearby_neurons) / len(nearby_neurons)
                neural_effect = avg_activation * mat_data['neural_conductivity']
                t = max(0, t + neural_effect * 0.3)
        
        # 5. Dimensional phase effects
        if mat_data['dimensional_phase'] != 0:
            phase_wave = math.sin(self.absolute.tick * 0.05 + hit_x * 0.1 + hit_y * 0.1)
            dimensional_shift = phase_wave * mat_data['dimensional_phase'] * 0.2
            t = max(0, min(0.99, t + dimensional_shift))
        
        # 6. Time dilation from multiple sources
        time_factor = self.godlike.get_effect_multiplier()
        if time_factor < 0.8:
            t = t * (1.5 - time_factor)
        
        # 7. Final enhanced character selection
        emotion_palette = self.godlike.get_emotion_palette(symbols)
        light_intensity = self.gfx.get_enhanced_light_intensity(hit_x, hit_y, world.map)
        
        t = max(0, t / light_intensity)
        
        idx = max(0, min(len(emotion_palette) - 1, int(t * (len(emotion_palette) - 1))))
        return emotion_palette[idx]

    def _render_absolute_objects(self, screen: List[str], world: World, enemies: List) -> List[str]:
        """Render objects with absolute consciousness effects"""
        
        # ABSOLUTE enhanced pickups with DNA/consciousness interaction
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
                    
                    # ABSOLUTE pickup effects
                    if p.kind == 'keycard':
                        # Reality key with consciousness resonance
                        if self.transcendent.consciousness_state.value == 'transcendent':
                            transcendent_keys = ['∞', '∅', '∴', '∵', '∷']
                            key_phase = (self.transcendent.tick // 8) % len(transcendent_keys)
                            sym = transcendent_keys[key_phase]
                        
                        # Holographic projection
                        if self.godlike.hologram_projection:
                            self.godlike.spawn_hologram_projection(sx, sy, 120)
                        
                        # Consciousness wave collapse
                        if self.absolute.consciousness_waves:
                            self.absolute.consciousness.collapse_wave_function(sx, sy)
                    
                    elif p.kind == 'health':
                        # Healing with chakra resonance  
                        healing_chars = ['♥', '♡', '❤', '♀', '⚕']
                        healing_phase = (self.transcendent.tick // 6) % len(healing_chars)
                        sym = healing_chars[healing_phase]
                        
                        # Spawn enlightenment particles
                        if self.transcendent.enlightenment_progress > 0.3:
                            self.transcendent.spawn_enlightenment_particles(p.x, p.y, 'healing_found')
                    
                    # Quantum glow with absolute enhancement
                    for offset in [-2, -1, 0, 1, 2]:
                        if 0 <= sx + offset < self.width:
                            line = screen[sy]
                            if offset == 0:
                                char = sym
                            elif abs(offset) == 1:
                                char = '◦'  # Inner glow
                            else:
                                char = '·'   # Outer glow
                            screen[sy] = line[:sx + offset] + char + line[sx + offset + 1:]
        
        return screen

    def _render_absolute_minimap(self, screen: List[str], world: World, enemies: List) -> List[str]:
        """ABSOLUTE minimap with consciousness and multiverse visualization"""
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
                
                # ABSOLUTE minimap with consciousness states
                if abs(mx - px) < 1 and abs(my - py) < 1:
                    # Player with transcendent states
                    if self.transcendent.consciousness_state.value == 'transcendent':
                        transcendent_chars = ['✪', '✫', '✦', '✧']
                        char = transcendent_chars[(self.transcendent.tick // 4) % len(transcendent_chars)]
                    elif self.transcendent.consciousness_state.value == 'enlightened':
                        enlightened_chars = ['◉', '◎', '◊', '○']
                        char = enlightened_chars[(self.transcendent.tick // 6) % len(enlightened_chars)]
                    elif self.meditation_time > 5.0:
                        meditative_chars = ['◎', '○', '◯', '◦']
                        char = meditative_chars[(self.transcendent.tick // 10) % len(meditative_chars)]
                    else:
                        char = '◎'
                
                elif world.map[my][mx] not in WALKABLE:
                    # Walls with absolute effects
                    if self.absolute.neural_networks and (mx // 5 * 5, my // 5 * 5) in self.absolute.neural_network:
                        neuron = self.absolute.neural_network[(mx // 5 * 5, my // 5 * 5)]
                        if neuron.activation > 0.7:
                            char = '✦'  # Firing neuron
                        else:
                            char = '■'
                    elif self.transcendent.fractal_architecture:
                        # Check for fractal nodes
                        is_fractal = any(abs(node.x - mx) < 2 and abs(node.y - my) < 2 
                                       for node in self.transcendent.fractal_nodes)
                        if is_fractal:
                            fractal_chars = ['◌', '◎', '◉', '⬟']
                            char = fractal_chars[(self.transcendent.tick // 8) % len(fractal_chars)]
                        else:
                            char = '■'
                    else:
                        char = '■'
                else:
                    # Open space with consciousness field
                    if (mx, my) in self.absolute.consciousness.cognitive_field:
                        field_data = self.absolute.consciousness.cognitive_field[(mx, my)]
                        if field_data['amplitude'] > 0.5:
                            char = '◉'
                        else:
                            char = '·'
                    else:
                        char = '·'
                
                screen[screen_y] = line[:screen_x] + char + line[screen_x + 1:]
        
        return screen

    def _overlay_meditation_interface(self, screen: List[str]):
        """Meditation interface for pacifist mode"""
        interface = [
            "    ◎ Consciousness ◎",
            f"  Meditation: {self.meditation_time:.1f}s",
            f"  Karma: {self.transcendent.karma_score:+.0f}"
        ]
        
        # Add consciousness state indicator
        state_symbols = {
            'normal': '○',
            'meditative': '◎', 
            'psychedelic': '◉',
            'enlightened': '✦',
            'transcendent': '✪'
        }
        
        state_char = state_symbols.get(self.transcendent.consciousness_state.value, '○')
        interface.append(f"  State: {state_char} {self.transcendent.consciousness_state.value.capitalize()}")
        
        base_row = self.height - len(interface) - 1
        for i, row in enumerate(interface):
            y = base_row + i
            if 0 <= y < self.height:
                start = 2  # Left side instead of weapon area
                line = screen[y]
                
                # Breathing effect for interface
                if (self.transcendent.tick % 40) < 20:
                    row = row.replace('◎', '◉')  # Pulse consciousness symbol
                
                row = row[:self.width - start]
                screen[y] = line[:start] + row + line[start+len(row):]

    def cast_ray_absolute(self, angle: float, world_map: List[str]) -> Tuple[float, str, int, int, float]:
        """ABSOLUTE ray casting with all dimensional effects"""
        ox = self.player.x
        oy = self.player.y
        dx = math.cos(angle)
        dy = math.sin(angle)
        step = 0.005  # Ultra-high precision for absolute effects
        dist = 0.0
        hit_x, hit_y = 0, 0
        surface_normal = 0.0
        
        # All quantum effects can affect ray casting
        tunneling_chance = 0.01 if self.godlike.quantum_tunneling else 0.0
        observer_effect = 0.02 if self.transcendent.observer_effect else 0.0
        dimensional_phase = 0.01 if self.absolute.hyperspatial_5d else 0.0
        
        while dist < self.max_depth:
            ox += dx * step
            oy += dy * step
            dist += step
            mx, my = int(ox), int(oy)
            
            # ABSOLUTE visited tracking with all effects
            if 0 <= mx < 100 and 0 <= my < 100:
                self.visited.add((mx, my))
                
                # Quantum uncertainty reveals adjacent
                if random.random() < tunneling_chance:
                    for dx_q in [-1, 0, 1]:
                        for dy_q in [-1, 0, 1]:
                            self.visited.add((mx + dx_q, my + dy_q))
                
                # Observer effect reveals distant areas
                if random.random() < observer_effect:
                    for dx_o in range(-3, 4):
                        for dy_o in range(-3, 4):
                            if abs(dx_o) + abs(dy_o) <= 3:
                                self.visited.add((mx + dx_o, my + dy_o))
            
            if my < 0 or my >= len(world_map) or mx < 0 or mx >= len(world_map[0]):
                return self.max_depth, 'void', mx, my, 0.0
            
            if world_map[my][mx] not in WALKABLE:
                # Multiple phase-through chances
                if (random.random() < tunneling_chance or 
                    random.random() < dimensional_phase):
                    continue
                
                surface_normal = math.atan2(my - self.player.y, mx - self.player.x)
                return dist, world_map[my][mx], mx, my, surface_normal
            
            hit_x, hit_y = mx, my
            
        return self.max_depth, 'void', hit_x, hit_y, surface_normal

    def move_player(self, key: str):
        """ABSOLUTE player movement with consciousness tracking"""
        self.visited.add((int(self.player.x), int(self.player.y)))
        
        speed = float(self.cfg.get('gameplay', {}).get('player_speed', 0.2))
        rot = float(self.cfg.get('gameplay', {}).get('rotate_speed', 0.2))
        
        # All time effects affect movement
        speed *= self.godlike.get_effect_multiplier()
        rot *= self.godlike.get_effect_multiplier()
        
        # Consciousness affects movement
        if self.transcendent.consciousness_state.value == 'transcendent':
            speed *= 1.5  # Transcendent movement
        elif self.transcendent.consciousness_state.value == 'meditative':
            speed *= 0.7  # Mindful movement
        
        if key == 'w':
            dx = speed * math.cos(self.player.angle)
            dy = speed * math.sin(self.player.angle)
            self.player.move(dx, dy)
            self.sound_events.append((int(self.player.x), int(self.player.y), 'footstep'))
            self.update_consciousness_state('forward_movement')
        elif key == 's':
            dx = -speed * math.cos(self.player.angle)
            dy = -speed * math.sin(self.player.angle)
            self.player.move(dx, dy)
            self.update_consciousness_state('backward_movement')
        elif key == 'a':
            self.player.rotate(-rot)
            self.update_consciousness_state('turn_left')
        elif key == 'd':
            self.player.rotate(rot)
            self.update_consciousness_state('turn_right')
        
        self.visited.add((int(self.player.x), int(self.player.y)))
        
        # Decision point for multiverse forking
        if self.absolute.multiverse_rendering:
            decision_msg = self.absolute.make_decision(f'movement_{key}')
            if decision_msg and self.banner_cb:
                self.banner_cb(decision_msg)

    def enter_meditation_mode(self):
        """Enter deep meditation state"""
        self.transcendent.enter_meditation_mode()
        
        if self.absolute.consciousness_waves:
            # Meditation creates strong consciousness field
            self.absolute.consciousness.collapse_wave_function(
                int(self.player.x), int(self.player.y)
            )
        
        if self.banner_cb:
            self.banner_cb('◎ Entering meditation ◎')

    def try_pickups(self, world: World):
        """ABSOLUTE pickup with consciousness evolution"""
        if not hasattr(world, 'pickups') or not world.pickups:
            return
        for p in world.pickups:
            if p.taken:
                continue
            if abs(p.x - self.player.x) < 0.5 and abs(p.y - self.player.y) < 0.5:
                p.taken = True
                
                # ABSOLUTE pickup effects with consciousness evolution
                self.gfx.spawn_sparks(p.x, p.y, 4)
                
                if p.kind == 'health':
                    self.player.heal(p.amount)
                    # Healing increases karma
                    self.transcendent.add_karma_points(5, 'self_care')
                    if self.banner_cb:
                        self.banner_cb('♥ Quantum healing acquired ♥')
                    
                elif p.kind == 'keycard':
                    # Reality keys advance enlightenment
                    enlightenment_msg = self.absolute.advance_enlightenment('cosmic_insight')
                    self.transcendent.spawn_enlightenment_particles(p.x, p.y, 'secret_found')
                    if self.banner_cb:
                        self.banner_cb('∞ Reality key acquired - Consciousness expanded ∞')
                
                elif p.kind == 'meditation_orb':  # New pickup type
                    self.meditation_time += 30.0
                    self.transcendent.add_karma_points(20, 'enlightenment_action')
                    if self.banner_cb:
                        self.banner_cb('✪ Meditation orb absorbed - Inner peace expanded ✪')

    # Compatibility methods enhanced
    def render_3d(self, world: World, enemies: List = None) -> List[str]:
        return self.render_3d_absolute(world, enemies)
    
    def correct_fish_eye(self, d: float, a: float) -> float:
        return d * math.cos(a - self.player.angle)
    
    def _shade(self, distance: float) -> str:
        if distance >= self.max_depth:
            return ' '
        t = distance / self.max_depth
        idx = int(t * (len(self.palette) - 1))
        return self.palette[idx]

    def _can_move_to(self, x: float, y: float) -> bool:
        return True

    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

# Ultimate compatibility - all systems available
RaycastingEngine = AbsoluteRaycastingEngine
UltimateRaycastingEngine = AbsoluteRaycastingEngine
GodlikeRaycastingEngine = AbsoluteRaycastingEngine