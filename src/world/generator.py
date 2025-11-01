"""
🌍 PROCEDURAL WORLD GENERATOR with doors, exits, and objectives
Infinite levels via Perlin noise, cellular automata, quantum seeds
"""

import random
import math
from typing import List, Tuple, Optional
from .pickups import spawn_pickups
from .objectives import place_doors_and_exits, generate_objectives

class ProceduralWorldGenerator:
    def __init__(self, seed: Optional[int] = None, config: dict | None = None):
        self.seed = seed or random.randint(0, 1000000)
        random.seed(self.seed)
        self.config = config or {}

        # World themes with progression scaling
        self.themes = {
            'quantum': {'walls': '#', 'floor': '.', 'special': 'Q', 'palette': [' ', '░', '▒', '▓', '█']},
            'atman': {'walls': '🕉', 'floor': '·', 'special': 'A', 'palette': [' ', '·', '∙', '•', '█']},
            'loqiemean': {'walls': '▓', 'floor': '~', 'special': 'L', 'palette': [' ', '~', '≈', '▓', '█']},
            'batut': {'walls': '█', 'floor': ' ', 'special': 'B', 'palette': [' ', '░', '▒', '▓', '█']}
        }

    def perlin_noise_2d(self, x: float, y: float) -> float:
        """Enhanced 2D Perlin noise with octaves"""
        result = 0.0
        frequency = 0.1
        amplitude = 1.0
        
        for _ in range(3):  # 3 octaves
            result += amplitude * (math.sin(x * frequency) * math.cos(y * frequency))
            frequency *= 2
            amplitude *= 0.5
        
        return result / 2.0

    def cellular_automata(self, width: int, height: int, iterations: int = 4, wall_prob: float = 0.45) -> List[List[str]]:
        """Enhanced cellular automata with configurable parameters"""
        grid = []
        for y in range(height):
            row = []
            for x in range(width):
                if (x == 0 or x == width-1 or y == 0 or y == height-1):
                    row.append('#')
                else:
                    row.append('#' if random.random() < wall_prob else '.')
            grid.append(row)
        
        for iteration in range(iterations):
            new_grid = [row[:] for row in grid]
            for y in range(1, height-1):
                for x in range(1, width-1):
                    wall_count = 0
                    for dy in range(-1, 2):
                        for dx in range(-1, 2):
                            if grid[y+dy][x+dx] == '#':
                                wall_count += 1
                    
                    # Progressive smoothing
                    threshold = 5 - (iteration // 2)  # Gets more aggressive
                    if wall_count >= threshold:
                        new_grid[y][x] = '#'
                    elif wall_count < 3:
                        new_grid[y][x] = '.'
            grid = new_grid
        
        return grid

    def generate_level(self, level: int):
        """Generate complete level with objectives"""
        from ..core.world import World
        
        # Progressive difficulty scaling
        prog_cfg = self.config.get('progression', {})
        difficulty_scale = float(prog_cfg.get('difficulty_scaling', 0.1))
        base_size = 12
        size = base_size + level * 2
        
        # Apply difficulty scaling to generation parameters
        wall_density = min(0.6, 0.45 + level * difficulty_scale * 0.1)
        iterations = min(6, 3 + level // 3)
        
        theme_names = list(self.themes.keys())
        theme_name = theme_names[level % len(theme_names)]
        theme = self.themes[theme_name]

        print(f"🎨 Generating {theme_name} world (level {level}, difficulty {difficulty_scale * level:.1f})...")

        # Generate base structure with scaled difficulty
        if level % 3 == 0:
            grid = self.cellular_automata(size, size, iterations, wall_density)
        else:
            grid = self.generate_perlin_world(size, size, level)

        # Convert to strings and apply theme
        world_map = []
        for row in grid:
            line = ''
            for cell in row:
                if cell == '#':
                    line += theme['walls']
                elif cell == '.':
                    line += theme['floor']
                else:
                    line += cell
            world_map.append(line)

        # Add special quantum elements
        self.add_special_elements(world_map, theme, level)

        # Place doors and exits
        doors, exits = place_doors_and_exits(world_map, self.config)
        
        # Spawn pickups with level scaling
        spawn_cfg = self.config.get('spawns', {}).copy()
        # Scale pickup chances with level (more sparse at higher levels)
        scale_factor = max(0.3, 1.0 - level * difficulty_scale)
        spawn_cfg['health_pack_chance'] = spawn_cfg.get('health_pack_chance', 0.08) * scale_factor
        spawn_cfg['ammo_pack_chance'] = spawn_cfg.get('ammo_pack_chance', 0.10) * scale_factor
        
        pickups = spawn_pickups(world_map, spawn_cfg)
        
        # Generate level objectives
        enemy_count = int(spawn_cfg.get('enemy_count', 6))
        objectives = generate_objectives(level, enemy_count, len(pickups))

        world = World(world_map, theme_name, level, self.seed)
        world.pickups = pickups
        world.doors = doors
        world.exits = exits
        world.objectives = objectives
        world.theme_palette = theme.get('palette', [' ', '░', '▒', '▓', '█'])
        
        return world

    def generate_perlin_world(self, width: int, height: int, level: int) -> List[List[str]]:
        """Generate world using enhanced Perlin noise"""
        grid = []
        
        # Level-based noise parameters
        complexity = min(0.3, 0.1 + level * 0.02)
        
        for y in range(height):
            row = []
            for x in range(width):
                if (x == 0 or x == width-1 or y == 0 or y == height-1):
                    row.append('#')
                else:
                    noise_value = self.perlin_noise_2d(x * complexity, y * complexity)
                    threshold = 0.3 + (level * 0.05)  # Higher levels = more walls
                    row.append('#' if noise_value > threshold else '.')
            grid.append(row)
        return grid

    def add_special_elements(self, world_map: List[str], theme: dict, level: int):
        """Add special quantum elements to world"""
        height = len(world_map)
        width = len(world_map[0])
        special_count = max(1, level // 2 + random.randint(0, 2))
        
        for _ in range(special_count):
            for _ in range(50):
                x = random.randint(1, width-2)
                y = random.randint(1, height-2)
                if world_map[y][x] == theme['floor']:
                    row = list(world_map[y])
                    row[x] = theme['special']
                    world_map[y] = ''.join(row)
                    break

    def get_spawn_positions(self, world_map: List[str]) -> List[Tuple[float, float]]:
        """Get valid spawn positions for enemies"""
        positions = []
        for y in range(len(world_map)):
            for x in range(len(world_map[0])):
                if world_map[y][x] in ['.', '·', '~']:
                    positions.append((x + 0.5, y + 0.5))
        return positions