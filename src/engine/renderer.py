"""
🎨 RAYCASTING RENDERER - Core 3D ASCII Engine
Optimized raycasting with fish-eye correction, textures, lighting
"""

import math
import os
from typing import List, Tuple, Optional
from ..core.player import Player
from ..core.world import World

class RaycastingEngine:
    def __init__(self, width: int = 80, height: int = 25):
        self.width = width
        self.height = height
        self.fov = math.pi / 3  # 60 degrees
        self.max_depth = 16.0

        # ASCII textures for different wall types
        self.wall_chars = {
            'stone': '█',
            'brick': '▓',
            'wood': '▒',
            'metal': '░'
        }

        # Lighting levels
        self.lighting = [' ', '░', '▒', '▓', '█']

        self.player = Player(x=1.5, y=1.5, angle=0)

    def cast_ray(self, angle: float, world_map: List[str]) -> Tuple[float, str]:
        """
        Cast single ray and return distance + wall type
        Optimized DDA algorithm for speed
        """
        ray_x = self.player.x
        ray_y = self.player.y

        dx = math.cos(angle)
        dy = math.sin(angle)

        # DDA step size optimization
        step = 0.02  # Smaller = more precise, slower
        distance = 0.0

        while distance < self.max_depth:
            ray_x += dx * step
            ray_y += dy * step
            distance += step

            map_x, map_y = int(ray_x), int(ray_y)

            # Bounds check
            if (map_y < 0 or map_y >= len(world_map) or 
                map_x < 0 or map_x >= len(world_map[0])):
                return self.max_depth, 'void'

            # Hit wall?
            if world_map[map_y][map_x] not in ['.', '·', '~', ' ']:
                wall_type = world_map[map_y][map_x]
                return distance, wall_type

        return self.max_depth, 'void'

    def correct_fish_eye(self, distance: float, angle: float) -> float:
        """Fix fish-eye distortion"""
        return distance * math.cos(angle - self.player.angle)

    def calculate_wall_height(self, distance: float) -> int:
        """Calculate wall height for rendering"""
        if distance <= 0.1:
            return self.height
        return min(self.height, int(self.height / distance))

    def get_wall_char(self, wall_type: str, distance: float) -> str:
        """Get ASCII character for wall with lighting"""
        base_char = self.wall_chars.get(wall_type, wall_type)

        # Apply lighting based on distance
        lighting_level = min(len(self.lighting) - 1, int(distance / 2))
        return self.lighting[lighting_level] if lighting_level < len(self.lighting) else ' '

    def render_3d(self, world: World, enemies: List = None) -> List[str]:
        """
        Main 3D rendering function
        Returns screen buffer as list of strings
        """
        if enemies is None:
            enemies = []
            
        screen = [' ' * self.width for _ in range(self.height)]

        # Render sky and floor
        for y in range(self.height // 2):
            screen[y] = '·' * self.width  # Sky
        for y in range(self.height // 2, self.height):
            screen[y] = '~' * self.width  # Floor

        # Render walls column by column
        for col in range(self.width):
            # Calculate ray angle
            ray_angle = (self.player.angle - self.fov / 2 + 
                        col / self.width * self.fov)

            # Cast ray
            distance, wall_type = self.cast_ray(ray_angle, world.map)

            # Apply fish-eye correction
            corrected_distance = self.correct_fish_eye(distance, ray_angle)

            # Calculate wall height
            wall_height = self.calculate_wall_height(corrected_distance)

            # Get wall character with lighting
            wall_char = self.get_wall_char(wall_type, corrected_distance)

            # Render wall column
            wall_start = max(0, self.height // 2 - wall_height // 2)
            wall_end = min(self.height, self.height // 2 + wall_height // 2)

            for row in range(wall_start, wall_end):
                screen[row] = screen[row][:col] + wall_char + screen[row][col+1:]

        # Render enemies
        screen = self.render_enemies(screen, enemies)

        return screen

    def render_enemies(self, screen: List[str], enemies: List) -> List[str]:
        """Render enemies as sprites"""
        for enemy in enemies:
            if not hasattr(enemy, 'alive') or not enemy.alive:
                continue

            # Calculate enemy screen position
            dx = enemy.x - self.player.x
            dy = enemy.y - self.player.y
            distance = math.sqrt(dx**2 + dy**2)

            if distance == 0:
                continue

            enemy_angle = math.atan2(dy, dx) - self.player.angle

            # Check if enemy is in FOV
            if abs(enemy_angle) < self.fov / 2:
                screen_x = int((enemy_angle + self.fov / 2) / self.fov * self.width)
                screen_y = self.height // 2

                if 0 <= screen_x < self.width:
                    enemy_char = enemy.get_sprite(distance) if hasattr(enemy, 'get_sprite') else '👾'
                    screen[screen_y] = (screen[screen_y][:screen_x] + 
                                      enemy_char + 
                                      screen[screen_y][screen_x+1:])

        return screen

    def move_player(self, key: str):
        """Move player based on input"""
        speed = 0.2

        if key == 'w':  # Forward
            dx = speed * math.cos(self.player.angle)
            dy = speed * math.sin(self.player.angle)
            self.player.move(dx, dy)
        elif key == 's':  # Backward
            dx = -speed * math.cos(self.player.angle)
            dy = -speed * math.sin(self.player.angle)
            self.player.move(dx, dy)
        elif key == 'a':  # Rotate left
            self.player.rotate(-0.2)
        elif key == 'd':  # Rotate right
            self.player.rotate(0.2)

    def player_shoot(self, enemies: List = None) -> bool:
        """Handle player shooting"""
        if enemies is None:
            enemies = []
            
        # Simple shooting: remove nearest enemy in crosshair
        hit_enemy = None
        min_distance = float('inf')

        for enemy in enemies:
            if not hasattr(enemy, 'alive') or not enemy.alive:
                continue

            dx = enemy.x - self.player.x
            dy = enemy.y - self.player.y
            distance = math.sqrt(dx**2 + dy**2)
            angle = math.atan2(dy, dx)
            angle_diff = abs(angle - self.player.angle)

            # Check if enemy is in crosshair (small angle tolerance)
            if angle_diff < 0.3 and distance < min_distance:
                min_distance = distance
                hit_enemy = enemy

        if hit_enemy and hasattr(hit_enemy, 'take_damage'):
            hit_enemy.take_damage(25)
            self.player.score += 10
            return True

        return False

    def clear_screen(self):
        """Clear terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
