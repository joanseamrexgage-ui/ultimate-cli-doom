"""
👤 PLAYER CLASS - Player state and actions
"""

import math

class Player:
    def __init__(self, x: float = 1.5, y: float = 1.5, angle: float = 0):
        self.x = x
        self.y = y
        self.angle = angle
        self.health = 100
        self.ammo = 50
        self.score = 0
        self.speed = 0.2
        self.rotation_speed = 0.2

    def move(self, dx: float, dy: float, world_map: list = None):
        """Move player with collision detection"""
        new_x = self.x + dx
        new_y = self.y + dy

        # Simple collision detection
        if world_map:
            map_x, map_y = int(new_x), int(new_y)
            if (0 <= map_x < len(world_map[0]) and 
                0 <= map_y < len(world_map) and
                world_map[map_y][map_x] in ['.', '·', '~', ' ']):
                self.x = new_x
                self.y = new_y
        else:
            self.x = new_x
            self.y = new_y

    def rotate(self, angle_delta: float):
        """Rotate player"""
        self.angle += angle_delta

        # Keep angle in range [0, 2π]
        while self.angle < 0:
            self.angle += 2 * math.pi
        while self.angle >= 2 * math.pi:
            self.angle -= 2 * math.pi

    def take_damage(self, damage: int):
        """Take damage"""
        self.health -= damage
        if self.health <= 0:
            self.health = 0

    def heal(self, amount: int):
        """Heal player"""
        self.health = min(100, self.health + amount)

    def add_ammo(self, amount: int):
        """Add ammo"""
        self.ammo += amount

    def shoot(self) -> bool:
        """Shoot (consumes ammo)"""
        if self.ammo > 0:
            self.ammo -= 1
            return True
        return False

    def get_stats(self) -> dict:
        """Get player stats for HUD"""
        return {
            'health': self.health,
            'ammo': self.ammo,
            'score': self.score,
            'position': (round(self.x, 1), round(self.y, 1)),
            'angle': round(math.degrees(self.angle), 1)
        }
