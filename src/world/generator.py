"""
🌍 PROCEDURAL WORLD GENERATOR with room-based architecture
Infinite levels via room + corridor system for better navigation
"""

import random
import math
from typing import List, Tuple, Optional
from .pickups import spawn_pickups
from .objectives import place_doors_and_exits, generate_objectives

class Room:
    def __init__(self, x: int, y: int, width: int, height: int, room_type: str = 'generic'):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.type = room_type  # 'spawn', 'armory', 'medical', 'reactor', 'storage', 'generic'
        self.connected = False
        
    def center(self) -> Tuple[int, int]:
        return (self.x + self.width // 2, self.y + self.height // 2)
        
    def overlaps(self, other: 'Room') -> bool:
        return not (self.x + self.width < other.x or 
                   other.x + other.width < self.x or
                   self.y + self.height < other.y or
                   other.y + other.height < self.y)

class ProceduralWorldGenerator:
    def __init__(self, seed: Optional[int] = None, config: dict = None):
        self.seed = seed or random.randint(0, 1000000)
        random.seed(self.seed)
        self.config = config or {}

        # Enhanced themes with material properties
        self.themes = {
            'quantum': {
                'walls': '#', 'floor': '.', 'special': 'Q', 'material': 'metal',
                'palette': [' ', '▒', '▓', '█'], 'floor_variants': ['.', '·', '¨']
            },
            'atman': {
                'walls': '🔹', 'floor': '·', 'special': 'A', 'material': 'stone',
                'palette': [' ', '·', '∘', '•', '█'], 'floor_variants': ['·', '∘', '°']
            },
            'loqiemean': {
                'walls': '▓', 'floor': '~', 'special': 'L', 'material': 'brick',
                'palette': [' ', '~', '≈', '▓', '█'], 'floor_variants': ['~', '≈', '∼']
            },
            'batut': {
                'walls': '█', 'floor': ' ', 'special': 'B', 'material': 'wood', 
                'palette': [' ', '░', '▒', '▓', '█'], 'floor_variants': [' ', '·', '`']
            }
        }

        # Room types with distinct purposes
        self.room_types = {
            'spawn': {'floor': '.', 'special_chance': 0.0},
            'armory': {'floor': '∘', 'special_chance': 0.3},
            'medical': {'floor': '+', 'special_chance': 0.2},
            'reactor': {'floor': '≈', 'special_chance': 0.8},
            'storage': {'floor': '□', 'special_chance': 0.1},
            'generic': {'floor': '·', 'special_chance': 0.1}
        }

    def generate_rooms(self, width: int, height: int, level: int) -> List[Room]:
        """Generate room layout for better navigation"""
        rooms = []
        
        world_cfg = self.config.get('world', {})
        room_enabled = bool(world_cfg.get('room_gen_enabled', True))
        if not room_enabled:
            return []  # Fallback to cellular automata
            
        room_min = int(world_cfg.get('room_min', 4))
        room_max = int(world_cfg.get('room_max', 7))
        room_size_min = int(world_cfg.get('room_size_min', 4))
        room_size_max = int(world_cfg.get('room_size_max', 8))
        
        num_rooms = random.randint(room_min, room_max)
        attempts = 0
        max_attempts = 100
        
        # First room is always spawn
        spawn_room = Room(1, 1, 
                         random.randint(room_size_min, room_size_max),
                         random.randint(room_size_min, room_size_max), 
                         'spawn')
        rooms.append(spawn_room)
        
        # Generate other rooms
        room_type_pool = ['generic'] * 3 + ['armory', 'medical', 'storage'] + (['reactor'] if level >= 3 else [])
        
        while len(rooms) < num_rooms and attempts < max_attempts:
            attempts += 1
            
            # Random position and size
            rw = random.randint(room_size_min, room_size_max)
            rh = random.randint(room_size_min, room_size_max)
            rx = random.randint(2, max(3, width - rw - 2))
            ry = random.randint(2, max(3, height - rh - 2))
            
            new_room = Room(rx, ry, rw, rh, random.choice(room_type_pool))
            
            # Check overlap with existing rooms (allow small gap)
            overlap = False
            for existing in rooms:
                expanded_existing = Room(existing.x - 1, existing.y - 1, 
                                       existing.width + 2, existing.height + 2)
                if new_room.overlaps(expanded_existing):
                    overlap = True
                    break
            
            if not overlap:
                rooms.append(new_room)
        
        return rooms

    def carve_rooms(self, grid: List[List[str]], rooms: List[Room], theme: dict) -> dict:
        """Carve rooms into grid and return room metadata"""
        room_data = {}
        
        for room in rooms:
            # Carve room interior
            for y in range(room.y, room.y + room.height):
                for x in range(room.x, room.x + room.width):
                    if 0 <= y < len(grid) and 0 <= x < len(grid[0]):
                        room_info = self.room_types.get(room.type, self.room_types['generic'])
                        grid[y][x] = room_info['floor']
            
            # Add special elements based on room type
            room_info = self.room_types.get(room.type, self.room_types['generic'])
            special_chance = room_info['special_chance']
            
            if special_chance > 0 and random.random() < special_chance:
                # Place special element in room center
                cx, cy = room.center()
                if 0 <= cy < len(grid) and 0 <= cx < len(grid[0]):
                    grid[cy][cx] = theme['special']
            
            room_data[room.type] = room_data.get(room.type, 0) + 1
        
        return room_data

    def connect_rooms(self, grid: List[List[str]], rooms: List[Room]):
        """Connect rooms with corridors using simple pathfinding"""
        if len(rooms) < 2:
            return
            
        # Connect each room to the nearest unconnected room
        rooms[0].connected = True
        
        while any(not room.connected for room in rooms):
            # Find closest connected-unconnected room pair
            best_dist = float('inf')
            best_pair = None
            
            for connected in [r for r in rooms if r.connected]:
                for unconnected in [r for r in rooms if not r.connected]:
                    c1 = connected.center()
                    c2 = unconnected.center()
                    dist = abs(c1[0] - c2[0]) + abs(c1[1] - c2[1])
                    if dist < best_dist:
                        best_dist = dist
                        best_pair = (connected, unconnected)
            
            if best_pair:
                self.carve_corridor(grid, best_pair[0].center(), best_pair[1].center())
                best_pair[1].connected = True

    def carve_corridor(self, grid: List[List[str]], start: Tuple[int, int], end: Tuple[int, int]):
        """Carve L-shaped corridor between two points"""
        sx, sy = start
        ex, ey = end
        
        # Horizontal first, then vertical
        if sx < ex:
            for x in range(sx, ex + 1):
                if 0 <= sy < len(grid) and 0 <= x < len(grid[0]):
                    grid[sy][x] = '.'
        else:
            for x in range(ex, sx + 1):
                if 0 <= sy < len(grid) and 0 <= x < len(grid[0]):
                    grid[sy][x] = '.'
        
        # Vertical
        if sy < ey:
            for y in range(sy, ey + 1):
                if 0 <= y < len(grid) and 0 <= ex < len(grid[0]):
                    grid[y][ex] = '.'
        else:
            for y in range(ey, sy + 1):
                if 0 <= y < len(grid) and 0 <= ex < len(grid[0]):
                    grid[y][ex] = '.'

    def generate_level(self, level: int):
        """Generate complete level with room-based architecture"""
        from ..core.world import World
        
        # Progressive difficulty scaling
        prog_cfg = self.config.get('progression', {})
        difficulty_scale = float(prog_cfg.get('difficulty_scaling', 0.1))
        base_size = 14
        size = base_size + level * 2
        
        theme_names = list(self.themes.keys())
        theme_name = theme_names[level % len(theme_names)]
        theme = self.themes[theme_name]

        print(f"🎨 Generating {theme_name} world (level {level}, {size}x{size})...")

        # Initialize with walls
        grid = [['#' for _ in range(size)] for _ in range(size)]
        
        # Generate and carve rooms
        rooms = self.generate_rooms(size, size, level)
        room_data = self.carve_rooms(grid, rooms, theme)
        
        if rooms:
            print(f"🏗️  Generated {len(rooms)} rooms: {room_data}")
            self.connect_rooms(grid, rooms)
        else:
            # Fallback to cellular automata if rooms disabled
            print("🌊 Using cellular automata generation...")
            grid = self.cellular_automata(size, size)

        # Convert to strings and apply theme
        world_map = []
        for row in grid:
            line = ''
            for cell in row:
                if cell == '#':
                    line += theme['walls']
                else:
                    line += cell
            world_map.append(line)

        # Place doors and exits
        doors, exits = place_doors_and_exits(world_map, self.config)
        
        # Spawn pickups with room awareness
        spawn_cfg = self.config.get('spawns', {}).copy()
        scale_factor = max(0.3, 1.0 - level * difficulty_scale * 0.1)
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
        world.rooms = rooms
        world.theme_palette = theme.get('palette', [' ', '▒', '▓', '█'])
        world.material = theme.get('material', 'stone')
        
        return world

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
                    
                    threshold = 5 - (iteration // 2)
                    if wall_count >= threshold:
                        new_grid[y][x] = '#'
                    elif wall_count < 3:
                        new_grid[y][x] = '.'
            grid = new_grid
        
        return grid

    def get_spawn_positions(self, world_map: List[str]) -> List[Tuple[float, float]]:
        """Get valid spawn positions for enemies"""
        positions = []
        for y in range(len(world_map)):
            for x in range(len(world_map[0])):
                if world_map[y][x] in ['.', '·', '~', '∘', '+', '□']:
                    positions.append((x + 0.5, y + 0.5))
        return positions