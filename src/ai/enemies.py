"""
Enemies with simple behavior for Ultimate CLI DOOM
"""

import math
import random

WALKABLE = {'.', '·', '~', ' '}

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
                if ch in WALKABLE:
                    positions.append((x + 0.5, y + 0.5))
        random.shuffle(positions)

        for i in range(min(count, len(positions))):
            px, py = positions[i]
            spawns.append(Enemy(px, py))
        return spawns

    def update(self, enemies, player, world=None):
        for e in enemies:
            if not e.alive:
                continue
            # simple chase behavior
            dx = player.x - e.x
            dy = player.y - e.y
            dist = math.hypot(dx, dy)
            if dist <= 0.1:
                continue

            step = 0.05
            nx = e.x + step * (dx / dist)
            ny = e.y + step * (dy / dist)

            # basic collision: only move if next tile is walkable
            if world is not None and hasattr(world, 'map') and world.map:
                tx, ty = int(nx), int(ny)
                if 0 <= ty < len(world.map) and 0 <= tx < len(world.map[0]):
                    if world.map[ty][tx] in WALKABLE:
                        e.x, e.y = nx, ny
                    # else: blocked by wall; skip movement
                # else: out of bounds; skip
            else:
                # no world info; move anyway
                e.x, e.y = nx, ny
