"""
🎮 ULTIMATE CLI DOOM - Enhanced Game Loop with AI integration
Координирует все системы: engine, world, AI, network
"""

import sys
from .engine.renderer import RaycastingEngine
from .world.generator import ProceduralWorldGenerator
from .ai.enemies import AdvancedEnemyAI
from .audio.sound import ASCIISoundSystem
from .ui.hud import GameHUD

try:
    import tomllib as toml
except Exception:
    toml = None

class MultiplayerManager:
    def connect(self): pass
    def sync_state(self): pass
    def disconnect(self): pass

class UltimateCliDoom:
    def __init__(self, width=80, height=25, dev_mode=False, multiplayer=False, config_path='config.toml'):
        self.width = width
        self.height = height
        self.dev_mode = dev_mode
        self.multiplayer_enabled = multiplayer
        self.config_path = config_path
        
        # Load config
        self.config = {}
        if toml is not None:
            try:
                with open(config_path, 'rb') as f:
                    self.config = toml.load(f)
            except Exception:
                self.config = {}

        # Initialize systems with config
        self.engine = RaycastingEngine(width, height, config_path)
        self.world_gen = ProceduralWorldGenerator(config=self.config)
        self.enemy_ai = AdvancedEnemyAI(config=self.config)
        self.sound = ASCIISoundSystem()
        self.hud = GameHUD(width, height)

        # Wire feedback callbacks
        self.engine.banner_cb = lambda text: self.hud.notify(text)
        self.engine.flash_cb = lambda: self.hud.damage_flash()
        self.engine.damage_direction_cb = lambda angle: self.hud.set_damage_direction(angle)

        if multiplayer:
            self.multiplayer = MultiplayerManager()

        self.running = True
        self.paused = False
        self.current_level = 1
        self.tick = 0
        self.weapon_mode = 'pistol'  # 'pistol' | 'shotgun' | 'rocket'
        
        # Level objectives
        self.objectives = {
            'kill_count': 0,
            'pickup_count': 0,
            'target_kills': 0,
            'target_pickups': 0
        }

    def run(self):
        self.initialize()
        while self.running:
            self.update()
            self.render()
            self.handle_input()
        self.cleanup()

    def initialize(self):
        print("🌌 Generating quantum world...")
        self.world = self.world_gen.generate_level(self.current_level)
        
        # Set level objectives
        spawn_cfg = self.config.get('spawns', {})
        enemy_count = int(spawn_cfg.get('enemy_count', 6))
        self.objectives['target_kills'] = max(enemy_count // 2, 3)
        self.objectives['target_pickups'] = 2
        
        print("🤖 Spawning enemies...")
        self.enemies = self.enemy_ai.spawn_enemies(self.world, count=enemy_count)
        
        print("🔊 Initializing sound...")
        self.sound.initialize()
        
        # Set initial objective direction
        self._update_objective_direction()
        
        if self.multiplayer_enabled:
            print("🌐 Connecting to network...")
            self.multiplayer.connect()

    def _update_objective_direction(self):
        """Update HUD compass objective direction"""
        # Find nearest keycard or enemy
        nearest_keycard = None
        nearest_enemy = None
        min_keycard_dist = float('inf')
        min_enemy_dist = float('inf')
        
        # Check keycards
        for pickup in getattr(self.world, 'pickups', []):
            if not pickup.taken and pickup.kind == 'keycard':
                dist = abs(pickup.x - self.engine.player.x) + abs(pickup.y - self.engine.player.y)
                if dist < min_keycard_dist:
                    min_keycard_dist = dist
                    nearest_keycard = pickup
        
        # Check enemies
        alive_enemies = [e for e in self.enemies if getattr(e, 'alive', False)]
        for enemy in alive_enemies:
            dist = abs(enemy.x - self.engine.player.x) + abs(enemy.y - self.engine.player.y)
            if dist < min_enemy_dist:
                min_enemy_dist = dist
                nearest_enemy = enemy
        
        # Set objective
        if nearest_keycard:
            dx = nearest_keycard.x - self.engine.player.x
            dy = nearest_keycard.y - self.engine.player.y
            angle = math.atan2(dy, dx)
            self.hud.set_objective(angle, "GET KEY")
        elif len(alive_enemies) > 0:
            if nearest_enemy:
                dx = nearest_enemy.x - self.engine.player.x
                dy = nearest_enemy.y - self.engine.player.y
                angle = math.atan2(dy, dx)
                self.hud.set_objective(angle, f"KILL {len(alive_enemies)}")
        else:
            self.hud.set_objective(None, "LEVEL CLEAR!")

    def update(self):
        if self.paused:
            return
        self.tick += 1
        
        # Update enemies and handle damage to player
        self.enemy_ai.update(self.enemies, self.engine.player, world=self.world)
        
        # Update projectiles
        self.engine.update_projectiles(self.world, self.enemies)
        self.engine.update_enemy_bullets(self.enemies)
        
        # Update pickups
        self.engine.try_pickups(self.world)
        
        # Update objectives
        self._update_objective_direction()
        
        # Passive score
        if self.tick % 100 == 0:
            self.engine.player.score += 1
            
        if self.multiplayer_enabled:
            self.multiplayer.sync_state()

    def render(self):
        self.engine.clear_screen()
        frame = self.engine.render_3d(self.world, self.enemies)
        frame = self.hud.add_overlay(frame, {
            'level': self.current_level,
            'health': self.engine.player.health,
            'ammo': self.engine.player.ammo,
            'score': self.engine.player.score
        }, player_angle=self.engine.player.angle)
        
        for line in frame:
            print(line)

    def handle_input(self):
        try:
            key = input().lower().strip()
            if key == 'q':
                self.quit_game()
            elif key == 'p':
                self.toggle_pause()
            elif key == 'm':
                self.show_map()
            elif key in ['w', 'a', 's', 'd']:
                self.engine.move_player(key)
            elif key == ' ':
                if self.engine.player_shoot(self.enemies, mode=self.weapon_mode):
                    self.sound.play_shoot()
                    self.hud.muzzle_flash()
            elif key == '1':
                self.weapon_mode = 'pistol'
                self.hud.notify('Pistol')
            elif key == '2':
                self.weapon_mode = 'shotgun'
                self.hud.notify('Shotgun')
            elif key == '3':
                self.weapon_mode = 'rocket'
                self.hud.notify('Rocket')
            elif key == 'h':
                self.engine.player.heal(10)
            elif key == 'e':
                self.engine.player.take_damage(10)
                self.engine.damage_feedback()
        except KeyboardInterrupt:
            self.quit_game()
        except:
            pass

    def quit_game(self):
        print("🕉️ Saving quantum state...")
        self.running = False

    def toggle_pause(self):
        self.paused = not self.paused
        status = "PAUSED" if self.paused else "RESUMED"
        print(f"⏸️ Game {status}")

    def show_map(self):
        map_view = self.world.generate_ascii_map()
        print("\n📍 QUANTUM MAP:")
        for line in map_view:
            print(line)
        input("Press Enter to continue...")

    def cleanup(self):
        if self.multiplayer_enabled:
            self.multiplayer.disconnect()
        print("🌌 Quantum reality collapsed. OM TAT SAT.")