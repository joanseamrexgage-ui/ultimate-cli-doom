"""
Enemies with simple behavior for Ultimate CLI DOOM
"""

import math
import random

class Enemy:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
        self.health = 50
        self.alive = True

    def get_sprite(self, distance: float) -> str:
        if distance < 2:
            return '💀'
        elif distance < 5:
            return '👹'
        return '👾'

    def take_damage(self, dmg: int):
        if not self.alive:
            return
        self.health -= dmg
        if self.health <= 0:
            self.alive = False

class SimpleEnemyAI:
    def spawn_enemies(self, world, count: int = 5):
        spawns = []
        positions = []

        # find spawnable tiles
        for y, row in enumerate(world.map):
            for x, ch in enumerate(row):
                if ch in ['.', '·', '~', ' ']:
                    positions.append((x + 0.5, y + 0.5))
        random.shuffle(positions)

        for i in range(min(count, len(positions))):
            px, py = positions[i]
            spawns.append(Enemy(px, py))
        return spawns

    def update(self, enemies, player):
        for e in enemies:
            if not e.alive:
                continue
            # simple chase behavior
            dx = player.x - e.x
            dy = player.y - e.y
            dist = math.hypot(dx, dy)
            if dist > 0.1:
                e.x += 0.05 * (dx / dist)
                e.y += 0.05 * (dy / dist)
