"""
ABSOLUTE ASCII GRAPHICS Renderer
Beyond transcendence: Multiverse, 5D hyperspatial, consciousness waves
"""

import math
import os
import random
from collections import deque
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
        self.weapon_overlay_enabled = bool(g.get('weapon_overlay', False))
        self.camera_shake = bool(g.get('camera_shake', True))
        
        # Navigation aids (always enabled)
        self.minimap_enabled = bool(g.get('minimap_enabled', True))
        self.minimap_width = int(g.get('minimap_width', 15))
        self.minimap_height = int(g.get('minimap_height', 8))
        self.materials_enabled = bool(g.get('materials_enabled', True))
        
        # Initialize ALL graphics systems
        try:
            self.gfx = NextGenGraphicsFX(self.cfg)
        except:
            self.gfx = None
        
        try:
            self.godlike = GodlikeGraphicsFX(self.cfg)
        except:
            self.godlike = None
        
        try:
            self.transcendent = TranscendentGraphicsFX(self.cfg)
        except:
            self.transcendent = None
        
        try:
            self.absolute = AbsoluteGraphicsEngine(self.cfg)
        except:
            self.absolute = None
        
        # Enhanced tracking
        self.visited = set()
        self.player_velocity = 0.0
        self.last_player_pos = (0.0, 0.0)
        self.sound_events = []
        self.meditation_time = 0.0
        self.player_actions = []
        self.observer_angle_history = deque(maxlen=10)
        
        self.player = Player(x=1.5, y=1.5, angle=0)
        self.shake_ttl = 0
        self.projectiles = []
        self.banner_cb = None
        self.flash_cb = None

    def render_3d(self, world: World, enemies: List = None) -> List[str]:
        """Main render function with graceful degradation"""
        if enemies is None:
            enemies = []  # Pacifist mode
        
        # Update systems that are available
        if self.gfx:
            self.gfx.update()
        if self.godlike:
            self.godlike.update(getattr(self.player, 'health', 100), self.player_velocity)
        if self.transcendent:
            self.transcendent.update(getattr(self.player, 'health', 100), self.player_actions, self.meditation_time)
        
        # Initialize screen
        screen = [' ' * self.width for _ in range(self.height)]
        
        # Basic raycasting
        for col in range(self.width):
            ray_angle = (self.player.angle - self.fov / 2 + col / self.width * self.fov)
            distance = self.cast_ray_basic(ray_angle, world.map)
            cd = distance * math.cos(ray_angle - self.player.angle)
            wall_height = self.height if cd <= 0.1 else min(self.height, int(self.height / cd))
            
            # Basic shading
            if distance >= self.max_depth:
                ch = ' '
            else:
                t = distance / self.max_depth
                idx = int(t * (len(self.palette) - 1))
                ch = self.palette[idx]
            
            y0 = max(0, self.height // 2 - wall_height // 2)
            y1 = min(self.height, self.height // 2 + wall_height // 2)
            
            for row in range(y0, y1):
                line = screen[row]
                screen[row] = line[:col] + ch + line[col+1:]
        
        # Basic floor
        for y in range(self.height // 2, self.height):
            floor_line = ''
            for x in range(self.width):
                if random.random() < 0.1:
                    floor_line += self.floor_char
                else:
                    floor_line += ' '
            screen[y] = floor_line
        
        # Apply available effects
        if self.gfx:
            try:
                screen = self.gfx.apply_bloom(screen)
            except:
                pass
        
        if self.transcendent:
            try:
                screen = self.transcendent.apply_karma_visualization(screen)
            except:
                pass
        
        if self.absolute:
            try:
                player_state = {
                    'x': self.player.x, 'y': self.player.y, 
                    'health': getattr(self.player, 'health', 100),
                    'karma': 0
                }
                screen = self.absolute.render_absolute_effects(screen, player_state)
            except:
                pass
        
        # Basic minimap
        if self.minimap_enabled:
            screen = self._render_basic_minimap(screen, world)
        
        return screen
    
    def cast_ray_basic(self, angle: float, world_map: List[str]) -> float:
        """Basic ray casting with error handling"""
        ox = self.player.x
        oy = self.player.y
        dx = math.cos(angle)
        dy = math.sin(angle)
        step = 0.1
        dist = 0.0
        
        while dist < self.max_depth:
            ox += dx * step
            oy += dy * step
            dist += step
            mx, my = int(ox), int(oy)
            
            if my < 0 or my >= len(world_map) or mx < 0 or mx >= len(world_map[0]):
                return self.max_depth
            
            if world_map[my][mx] not in WALKABLE:
                return dist
            
            self.visited.add((mx, my))
        
        return self.max_depth
    
    def _render_basic_minimap(self, screen: List[str], world: World) -> List[str]:
        """Basic minimap with error handling"""
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
                    
                char = '?'
                
                if abs(mx - px) < 1 and abs(my - py) < 1:
                    char = '◎'  # Player
                elif (mx, my) in self.visited:
                    if world.map[my][mx] not in WALKABLE:
                        char = '■'  # Wall
                    else:
                        char = '·'  # Floor
                
                screen[screen_y] = line[:screen_x] + char + line[screen_x + 1:]
        
        return screen
    
    def move_player(self, key: str):
        """Basic movement with error handling"""
        self.visited.add((int(self.player.x), int(self.player.y)))
        
        speed = 0.2
        rot = 0.2
        
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
    
    def try_pickups(self, world: World):
        """Basic pickup handling"""
        if not hasattr(world, 'pickups') or not world.pickups:
            return
        for p in world.pickups:
            if p.taken:
                continue
            if abs(p.x - self.player.x) < 0.5 and abs(p.y - self.player.y) < 0.5:
                p.taken = True
                
                if p.kind == 'health':
                    self.player.heal(p.amount)
                    if self.banner_cb:
                        self.banner_cb('♥ Health restored')
                elif p.kind == 'keycard':
                    if self.banner_cb:
                        self.banner_cb('∞ Key acquired')
    
    def enter_meditation_mode(self):
        """Enter meditation state"""
        if self.banner_cb:
            self.banner_cb('◎ Entering meditation ◎')
    
    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def player_shoot(self, enemies: List = None, mode: str = 'pistol') -> bool:
        """No shooting in pacifist mode"""
        return False
    
    def update_projectiles(self, world: World, enemies: List):
        """No projectiles in pacifist mode"""
        pass
    
    def update_enemy_bullets(self, enemies: List) -> bool:
        """No enemy bullets in pacifist mode"""
        return False

# Compatibility aliases - CRITICAL for import resolution
RaycastingEngine = AbsoluteRaycastingEngine
UltimateRaycastingEngine = AbsoluteRaycastingEngine
GodlikeRaycastingEngine = AbsoluteRaycastingEngine