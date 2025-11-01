"""
🎮 ULTIMATE CLI DOOM - Complete Game with Objectives & Progression
Координирует все системы: engine, world, AI, network
"""

import sys
import math
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
        self.weapon_mode = 'pistol'
        self.has_keycard = False
        
        # Statistics tracking
        self.stats = {
            'total_kills': 0,
            'total_pickups': 0,
            'levels_completed': 0,
            'shots_fired': 0,
            'damage_taken': 0
        }

    def run(self):
        self.initialize()
        while self.running:
            self.update()
            self.render()
            self.handle_input()
        self.cleanup()

    def initialize(self):
        print(f"🌌 Generating quantum world (Level {self.current_level})...")
        self.world = self.world_gen.generate_level(self.current_level)
        
        # Scale enemy count with level
        spawn_cfg = self.config.get('spawns', {})
        base_enemies = int(spawn_cfg.get('enemy_count', 6))
        max_enemies = int(self.config.get('progression', {}).get('max_enemies_per_level', 12))
        enemy_count = min(max_enemies, base_enemies + self.current_level)
        
        print(f"🤖 Spawning {enemy_count} enemies...")
        self.enemies = self.enemy_ai.spawn_enemies(self.world, count=enemy_count)
        
        print("🔊 Initializing sound...")
        self.sound.initialize()
        
        # Reset level state
        self.has_keycard = False
        
        # Show objectives
        if hasattr(self.world, 'objectives'):
            print("\n🎯 MISSION OBJECTIVES:")
            for obj in self.world.objectives:
                print(f"  • {obj.progress_text()}")
        
        self._update_objective_direction()
        
        if self.multiplayer_enabled:
            print("🌐 Connecting to network...")
            self.multiplayer.connect()

    def _update_objective_direction(self):
        """Update HUD compass objective direction"""
        if not hasattr(self.world, 'doors') or not hasattr(self.world, 'exits'):
            return
            
        # Priority: keycard > door > exit > enemy
        player_x, player_y = self.engine.player.x, self.engine.player.y
        
        if not self.has_keycard:
            # Look for keycard
            for pickup in getattr(self.world, 'pickups', []):
                if not pickup.taken and pickup.kind == 'keycard':
                    dx = pickup.x - player_x
                    dy = pickup.y - player_y
                    angle = math.atan2(dy, dx)
                    self.hud.set_objective(angle, "GET KEY")
                    return
        else:
            # Look for locked door to open
            for door in self.world.doors:
                if door.locked and not door.opened:
                    dx = door.x - player_x
                    dy = door.y - player_y
                    angle = math.atan2(dy, dx)
                    self.hud.set_objective(angle, "OPEN DOOR")
                    return
            
            # Check if objectives are complete
            all_complete = True
            if hasattr(self.world, 'objectives'):
                for obj in self.world.objectives:
                    if not obj.completed:
                        all_complete = False
                        break
            
            if all_complete:
                # Point to exit
                for exit_obj in self.world.exits:
                    if exit_obj.active:
                        dx = exit_obj.x - player_x
                        dy = exit_obj.y - player_y
                        angle = math.atan2(dy, dx)
                        self.hud.set_objective(angle, "EXIT")
                        return
        
        # Default: point to nearest enemy
        alive_enemies = [e for e in self.enemies if getattr(e, 'alive', False)]
        if alive_enemies:
            nearest = min(alive_enemies, key=lambda e: abs(e.x - player_x) + abs(e.y - player_y))
            dx = nearest.x - player_x
            dy = nearest.y - player_y
            angle = math.atan2(dy, dx)
            self.hud.set_objective(angle, f"KILL {len(alive_enemies)}")
        else:
            self.hud.set_objective(None, "CLEAR!")

    def _check_interactions(self):
        """Check for door/exit interactions"""
        px, py = self.engine.player.x, self.engine.player.y
        
        # Check doors
        if hasattr(self.world, 'doors'):
            for door in self.world.doors:
                if abs(door.x - px) < 0.8 and abs(door.y - py) < 0.8:
                    if door.locked and self.has_keycard:
                        door.locked = False
                        door.opened = True
                        self.has_keycard = False  # Use keycard
                        self.hud.notify("Door unlocked!")
                        # Update world map
                        row = list(self.world.map[door.y])
                        row[door.x] = '·'
                        self.world.map[door.y] = ''.join(row)
                    elif door.locked:
                        self.hud.notify("Need keycard")
        
        # Check exits
        if hasattr(self.world, 'exits'):
            for exit_obj in self.world.exits:
                if abs(exit_obj.x - px) < 0.8 and abs(exit_obj.y - py) < 0.8:
                    if exit_obj.active:
                        self._advance_level()
                    else:
                        self.hud.notify("Complete objectives first")

    def _advance_level(self):
        """Advance to next level"""
        self.current_level += 1
        self.stats['levels_completed'] += 1
        self.hud.notify(f"LEVEL {self.current_level}!", frames=60)
        print(f"\n✨ LEVEL {self.current_level} UNLOCKED! ✨")
        self.initialize()

    def _update_objectives(self):
        """Update objective progress and activate exits"""
        if not hasattr(self.world, 'objectives'):
            return
            
        # Count kills
        alive_enemies = sum(1 for e in self.enemies if getattr(e, 'alive', False))
        total_enemies = len(self.enemies)
        kills = total_enemies - alive_enemies
        
        # Count pickups taken
        taken_pickups = sum(1 for p in getattr(self.world, 'pickups', []) if p.taken)
        
        # Update objectives
        for obj in self.world.objectives:
            if obj.type == 'kill':
                obj.current = kills
            elif obj.type == 'collect':
                obj.current = taken_pickups
            elif obj.type == 'survive':
                obj.current = self.tick
            
            obj.completed = (obj.current >= obj.target)
        
        # Activate exits if all objectives complete
        all_complete = all(obj.completed for obj in self.world.objectives)
        if hasattr(self.world, 'exits'):
            for exit_obj in self.world.exits:
                exit_obj.active = all_complete

    def update(self):
        if self.paused:
            return
        self.tick += 1
        
        # Update enemies
        self.enemy_ai.update(self.enemies, self.engine.player, world=self.world)
        
        # Update projectiles
        self.engine.update_projectiles(self.world, self.enemies)
        self.engine.update_enemy_bullets(self.enemies)
        
        # Update pickups and check for keycard
        old_pickups = sum(1 for p in getattr(self.world, 'pickups', []) if p.taken)
        self.engine.try_pickups(self.world)
        new_pickups = sum(1 for p in getattr(self.world, 'pickups', []) if p.taken)
        
        # Check if keycard was picked up
        for p in getattr(self.world, 'pickups', []):
            if p.taken and p.kind == 'keycard':
                self.has_keycard = True
        
        # Check interactions
        self._check_interactions()
        
        # Update objectives
        self._update_objectives()
        
        # Update compass
        self._update_objective_direction()
        
        # Passive score
        if self.tick % 100 == 0:
            self.engine.player.score += 1
            
        if self.multiplayer_enabled:
            self.multiplayer.sync_state()

    def render(self):
        self.engine.clear_screen()
        frame = self.engine.render_3d(self.world, self.enemies)
        
        # Add objectives info to stats
        obj_text = ""
        if hasattr(self.world, 'objectives') and self.world.objectives:
            active_obj = next((obj for obj in self.world.objectives if not obj.completed), None)
            if active_obj:
                obj_text = active_obj.progress_text()
        
        frame = self.hud.add_overlay(frame, {
            'level': self.current_level,
            'health': self.engine.player.health,
            'ammo': self.engine.player.ammo,
            'score': self.engine.player.score,
            'weapon': self.weapon_mode.upper(),
            'objective': obj_text
        }, player_angle=self.engine.player.angle)
        
        for line in frame:
            print(line)
        
        # Show objective progress occasionally
        if self.tick % 200 == 0 and hasattr(self.world, 'objectives'):
            incomplete = [obj for obj in self.world.objectives if not obj.completed]
            if incomplete:
                self.hud.notify(incomplete[0].progress_text(), frames=45)

    def handle_input(self):
        try:
            key = input().lower().strip()
            if key == 'q':
                self.quit_game()
            elif key == 'p':
                self.toggle_pause()
            elif key == 'm':
                self.show_map()
            elif key == 'o':
                self.show_objectives()
            elif key in ['w', 'a', 's', 'd']:
                self.engine.move_player(key)
            elif key == ' ':
                if self.engine.player_shoot(self.enemies, mode=self.weapon_mode):
                    self.sound.play_shoot()
                    self.hud.muzzle_flash()
                    self.stats['shots_fired'] += 1
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
                self.stats['damage_taken'] += 10
        except KeyboardInterrupt:
            self.quit_game()
        except:
            pass

    def show_objectives(self):
        """Display current objectives"""
        print("\n🎯 MISSION OBJECTIVES:")
        if hasattr(self.world, 'objectives'):
            for obj in self.world.objectives:
                status = "✓" if obj.completed else "•"
                print(f"  {status} {obj.progress_text()}")
        else:
            print("  • Explore and survive")
        
        print(f"\n📈 STATISTICS:")
        print(f"  Shots fired: {self.stats['shots_fired']}")
        print(f"  Damage taken: {self.stats['damage_taken']}")
        print(f"  Levels completed: {self.stats['levels_completed']}")
        
        input("\nPress Enter to continue...")

    def quit_game(self):
        print("🕉️ Saving quantum state...")
        print(f"Final Score: {self.engine.player.score}")
        print(f"Levels Completed: {self.stats['levels_completed']}")
        self.running = False

    def toggle_pause(self):
        self.paused = not self.paused
        status = "PAUSED" if self.paused else "RESUMED"
        print(f"⏸️ Game {status}")
        
        if self.paused:
            print("\n🎮 CONTROLS:")
            print("  WASD - Move/Turn  | Space - Shoot | 1/2/3 - Weapons")
            print("  M - Map | O - Objectives | P - Pause | Q - Quit")

    def show_map(self):
        map_view = self.world.generate_ascii_map()
        print("\n📍 QUANTUM MAP:")
        for line in map_view:
            print(line)
        
        # Show legend
        print("\n🗺️ LEGEND:")
        print("  @ - You | 👹👺👾 - Enemies | + ∎ ⌘ - Pickups")
        print("  | - Door | > - Exit | # - Wall | . - Floor")
        
        input("\nPress Enter to continue...")

    def cleanup(self):
        if self.multiplayer_enabled:
            self.multiplayer.disconnect()
        print("🌌 Quantum reality collapsed. OM TAT SAT.")