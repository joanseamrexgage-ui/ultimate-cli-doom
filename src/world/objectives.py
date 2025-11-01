"""
🎯 Mission system with doors, exits, and level objectives
"""

import random
from typing import List, Tuple, Dict
from .pickups import Pickup

WALKABLE = {'.', '·', '~', ' '}
DOOR_SYMBOLS = {'|', '∥', '▐', '▌'}
EXIT_SYMBOLS = {'>', '»', '→'}

class Door:
    def __init__(self, x: int, y: int, locked: bool = True):
        self.x = x
        self.y = y
        self.locked = locked
        self.opened = False
    
        
    def symbol(self) -> str:
        if self.opened:
            return '·'  # Open space
        return '|' if self.locked else '∥'

class Exit:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
        self.active = False  # Becomes active when objectives complete
    
    def symbol(self) -> str:
        return '»' if self.active else '>'

class LevelObjective:
    def __init__(self, obj_type: str, target: int, description: str):
        self.type = obj_type  # 'kill', 'collect', 'survive'
        self.target = target
        self.current = 0
        self.description = description
        self.completed = False
    
    def update(self, value: int = 1):
        self.current = min(self.target, self.current + value)
        self.completed = (self.current >= self.target)
    
    def progress_text(self) -> str:
        return f"{self.description}: {self.current}/{self.target}"

def place_doors_and_exits(world_map: List[str], config: dict) -> Tuple[List[Door], List[Exit]]:
    """Place doors and exits in strategic locations"""
    doors: List[Door] = []
    exits: List[Exit] = []
    
    door_count = int(config.get('spawns', {}).get('door_count', 2))
    exit_count = int(config.get('spawns', {}).get('exit_count', 1))
    
    height = len(world_map)
    width = len(world_map[0])
    
    # Find wall positions suitable for doors (walls with adjacent walkable spaces)
    door_candidates: List[Tuple[int, int]] = []
    for y in range(1, height-1):
        for x in range(1, width-1):
            if world_map[y][x] not in WALKABLE:
                # Check if this wall has walkable spaces on opposite sides
                if ((world_map[y-1][x] in WALKABLE and world_map[y+1][x] in WALKABLE) or
                    (world_map[y][x-1] in WALKABLE and world_map[y][x+1] in WALKABLE)):
                    door_candidates.append((x, y))
    
    random.shuffle(door_candidates)
    
    # Place doors
    for i in range(min(door_count, len(door_candidates))):
        x, y = door_candidates[i]
        doors.append(Door(x, y, locked=True))
        # Modify world map
        row = list(world_map[y])
        row[x] = '|'
        world_map[y] = ''.join(row)
    
    # Find positions for exits (far from spawn, preferably corners)
    exit_candidates: List[Tuple[int, int, float]] = []
    spawn_x, spawn_y = 1.5, 1.5  # Assumed spawn
    
    for y in range(1, height-1):
        for x in range(1, width-1):
            if world_map[y][x] in WALKABLE:
                dist = abs(x - spawn_x) + abs(y - spawn_y)
                if dist > width // 2:  # Far from spawn
                    exit_candidates.append((x, y, dist))
    
    # Sort by distance, take furthest
    exit_candidates.sort(key=lambda pos: pos[2], reverse=True)
    
    # Place exits
    for i in range(min(exit_count, len(exit_candidates))):
        x, y, _ = exit_candidates[i]
        exits.append(Exit(x, y))
        # Modify world map
        row = list(world_map[y])
        row[x] = '>'
        world_map[y] = ''.join(row)
    
    return doors, exits

def generate_objectives(level: int, enemy_count: int, pickup_count: int) -> List[LevelObjective]:
    """Generate level objectives based on level and content"""
    objectives: List[LevelObjective] = []
    
    # Scale difficulty with level
    kill_target = max(2, enemy_count // 2 + level // 3)
    collect_target = max(1, pickup_count // 3)
    
    # Primary objective: always kill enemies
    objectives.append(LevelObjective('kill', kill_target, 'Eliminate hostiles'))
    
    # Secondary objectives based on level
    if level >= 2:
        objectives.append(LevelObjective('collect', collect_target, 'Collect items'))
    
    if level >= 5:
        # Survival challenge for higher levels
        survive_time = min(300, 120 + level * 15)  # 2-5 minutes
        objectives.append(LevelObjective('survive', survive_time, f'Survive {survive_time//60}m'))
    
    return objectives