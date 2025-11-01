"""
🤖 Advanced enemy AI with shooter behavior and telegraph system
"""

import math
import random

WALKABLE = {'.', '·', '~', ' '}

class Enemy:
    def __init__(self, x: float, y: float, enemy_type: str = 'runner'):
        self.x = x
        self.y = y
        self.health = 50
        self.alive = True
        self.type = enemy_type  # 'runner' | 'tank' | 'shooter'
        
        # Shooter-specific state
        self.state = 'idle'  # 'idle' | 'telegraph' | 'cooldown'
        self.state_timer = 0
        self.projectiles = []

    def get_sprite(self, distance: float) -> str:
        sprites = {
            'runner': {'close': '👹', 'mid': '👺', 'far': '👾'},
            'tank': {'close': '🛡', 'mid': '⚔️', 'far': '🏰'},
            'shooter': {'close': '🔴' if self.state == 'telegraph' else '🎯', 'mid': '⚡', 'far': '👁'}
        }
        
        sprite_set = sprites.get(self.type, sprites['runner'])
        if distance < 2:
            return sprite_set['close']
        elif distance < 5:
            return sprite_set['mid']
        return sprite_set['far']

    def take_damage(self, dmg: int):
        if not self.alive:
            return
        self.health -= dmg
        if self.health <= 0:
            self.alive = False

class AdvancedEnemyAI:
    def __init__(self, config: dict = None):
        self.config = config or {}
        
    def spawn_enemies(self, world, count: int = 6):
        spawns = []
        positions = []

        # Find spawnable tiles
        for y, row in enumerate(world.map):
            for x, ch in enumerate(row):
                if ch in WALKABLE:
                    positions.append((x + 0.5, y + 0.5))
        random.shuffle(positions)

        # Mix of enemy types based on config
        shooter_chance = float(self.config.get('ai', {}).get('shooter_spawn_chance', 0.3))
        tank_chance = float(self.config.get('ai', {}).get('tank_spawn_chance', 0.2))
        
        for i in range(min(count, len(positions))):
            px, py = positions[i]
            r = random.random()
            if r < shooter_chance:
                enemy_type = 'shooter'
            elif r < shooter_chance + tank_chance:
                enemy_type = 'tank'
            else:
                enemy_type = 'runner'
            
            enemy = Enemy(px, py, enemy_type)
            if enemy_type == 'tank':
                enemy.health = 100
            spawns.append(enemy)
        
        return spawns

    def update(self, enemies, player, world=None):
        for e in enemies:
            if not e.alive:
                continue
                
            if e.type == 'shooter':
                self._update_shooter(e, player, world)
            elif e.type == 'tank':
                self._update_tank(e, player, world)
            else:
                self._update_runner(e, player, world)

    def _update_runner(self, enemy, player, world):
        dx = player.x - enemy.x
        dy = player.y - enemy.y
        dist = math.hypot(dx, dy)
        if dist <= 0.1:
            return

        speed = float(self.config.get('ai', {}).get('runner_speed', 0.07))
        nx = enemy.x + speed * (dx / dist)
        ny = enemy.y + speed * (dy / dist)

        if self._can_move_to(nx, ny, world):
            enemy.x, enemy.y = nx, ny

    def _update_tank(self, enemy, player, world):
        dx = player.x - enemy.x
        dy = player.y - enemy.y
        dist = math.hypot(dx, dy)
        if dist <= 0.1:
            return

        speed = float(self.config.get('ai', {}).get('tank_speed', 0.03))
        nx = enemy.x + speed * (dx / dist)
        ny = enemy.y + speed * (dy / dist)

        if self._can_move_to(nx, ny, world):
            enemy.x, enemy.y = nx, ny

    def _update_shooter(self, enemy, player, world):
        ai_cfg = self.config.get('ai', {})
        telegraph_frames = int(ai_cfg.get('telegraph_frames', 30))
        fire_cooldown = int(ai_cfg.get('fire_cooldown', 60))
        bullet_speed = float(ai_cfg.get('bullet_speed', 0.4))
        
        # State machine
        if enemy.state == 'idle':
            # Check if player is in range and line of sight
            dx = player.x - enemy.x
            dy = player.y - enemy.y
            dist = math.hypot(dx, dy)
            
            if dist < 8.0 and random.random() < 0.02:  # 2% chance per tick to start attacking
                enemy.state = 'telegraph'
                enemy.state_timer = telegraph_frames
        
        elif enemy.state == 'telegraph':
            enemy.state_timer -= 1
            if enemy.state_timer <= 0:
                # Fire!
                dx = player.x - enemy.x
                dy = player.y - enemy.y
                dist = math.hypot(dx, dy)
                if dist > 0:
                    bullet_dx = bullet_speed * (dx / dist)
                    bullet_dy = bullet_speed * (dy / dist)
                    enemy.projectiles.append({
                        'x': enemy.x, 'y': enemy.y,
                        'dx': bullet_dx, 'dy': bullet_dy,
                        'alive': True
                    })
                enemy.state = 'cooldown'
                enemy.state_timer = fire_cooldown
        
        elif enemy.state == 'cooldown':
            enemy.state_timer -= 1
            if enemy.state_timer <= 0:
                enemy.state = 'idle'

        # Update projectiles
        damage = int(ai_cfg.get('bullet_damage', 15))
        for bullet in enemy.projectiles[:]:
            if not bullet.get('alive'):
                continue
            
            bullet['x'] += bullet['dx']
            bullet['y'] += bullet['dy']
            
            # Check collision with world
            if not self._can_move_to(bullet['x'], bullet['y'], world):
                bullet['alive'] = False
                continue
            
            # Check hit player
            if abs(bullet['x'] - player.x) < 0.3 and abs(bullet['y'] - player.y) < 0.3:
                bullet['alive'] = False
                player.take_damage(damage)
                # Direction for HUD indicator
                angle = math.atan2(bullet['dy'], bullet['dx'])
                return angle  # Return damage direction
        
        return None

    def _can_move_to(self, x: float, y: float, world) -> bool:
        if world is None or not hasattr(world, 'map') or not world.map:
            return True
        tx, ty = int(x), int(y)
        if 0 <= ty < len(world.map) and 0 <= tx < len(world.map[0]):
            return world.map[ty][tx] in WALKABLE
        return False

# Compatibility alias
SimpleEnemyAI = AdvancedEnemyAI