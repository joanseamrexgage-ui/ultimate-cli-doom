"""
🌍 PROCEDURAL WORLD GENERATOR
Infinite levels via Perlin noise, cellular automata, quantum seeds
"""

import random
import math
from typing import List, Tuple, Optional
from .pickups import spawn_pickups

class ProceduralWorldGenerator:
    def __init__(self, seed: Optional[int] = None, config: dict | None = None):
        self.seed = seed or random.randint(0, 1000000)
        random.seed(self.seed)
        self.config = config or {}

        # World themes (from our quantum night)
        self.themes = {
            'quantum': {'walls': '#', 'floor': '.', 'special': 'Q'},
            'atman': {'walls': '🕉', 'floor': '·', 'special': 'A'},
            'loqiemean': {'walls': '▓', 'floor': '~', 'special': 'L'},
            'batut': {'walls': '█', 'floor': ' ', 'special': 'B'}
        }

    def perlin_noise_2d(self, x: float, y: float) -> float:
        """Simple 2D Perlin noise implementation"""
        return (math.sin(x * 0.3) * math.cos(y * 0.3) + 
                math.sin(x * 0.7) * math.cos(y * 0.7) * 0.5) / 1.5

    def cellular_automata(self, width: int, height: int, iterations: int = 3) -> List[List[str]]:
        """Generate cave-like structures using cellular automata"""
        grid = []
        for y in range(height):
            row = []
            for x in range(width):
                if (x == 0 or x == width-1 or y == 0 or y == height-1):
                    row.append('#')  # Walls on edges
                else:
                    row.append('#' if random.random() < 0.45 else '.')
            grid.append(row)
        for _ in range(iterations):
            new_grid = [row[:] for row in grid]
            for y in range(1, height-1):
                for x in range(1, width-1):
                    wall_count = 0
                    for dy in range(-1, 2):
                        for dx in range(-1, 2):
                            if grid[y+dy][x+dx] == '#':
                                wall_count += 1
                    if wall_count >= 5:
                        new_grid[y][x] = '#'
                    elif wall_count < 4:
                        new_grid[y][x] = '.'
            grid = new_grid
        return grid

    def generate_level(self, level: int):
        """Generate complete level"""
        # Import here to avoid circular imports
        from ..core.world import World
        
        # Size based on level (progressive difficulty)
        base_size = 12
        size = base_size + level * 2

        # Choose theme based on level
        theme_names = list(self.themes.keys())
        theme_name = theme_names[level % len(theme_names)]
        theme = self.themes[theme_name]

        print(f"🎨 Generating {theme_name} world (level {level})...")

        # Generate base structure
        if level % 3 == 0:
            # Cellular automata caves
            grid = self.cellular_automata(size, size)
        else:
            # Perlin-based terrain
            grid = self.generate_perlin_world(size, size)

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

        # Spawn pickups according to config
        sp_cfg = self.config.get('spawns', {})
        pickups = spawn_pickups(world_map, sp_cfg)

        world = World(world_map, theme_name, level, self.seed)
        world.pickups = pickups
        return world

    def generate_perlin_world(self, width: int, height: int) -> List[List[str]]:
        """Generate world using Perlin noise"""
        grid = []
        for y in range(height):
            row = []
            for x in range(width):
                # Edge walls
                if (x == 0 or x == width-1 or y == 0 or y == height-1):
                    row.append('#')
                else:
                    # Use Perlin noise to determine terrain
                    noise_value = self.perlin_noise_2d(x * 0.1, y * 0.1)
                    row.append('#' if noise_value > 0.3 else '.')
            grid.append(row)
        return grid

    def add_special_elements(self, world_map: List[str], theme: dict, level: int):
        """Add special quantum elements to world"""
        height = len(world_map)
        width = len(world_map[0])
        special_count = max(1, level // 2)
        for _ in range(special_count):
            for _ in range(50):  # Max attempts
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
