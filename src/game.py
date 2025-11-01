"""
🎮 ULTIMATE CLI DOOM - Main Game Class
Координирует все системы: engine, world, AI, network
"""

import sys
from .engine.renderer import RaycastingEngine
from .world.generator import ProceduralWorldGenerator
from .ai.enemies import SimpleEnemyAI
from .audio.sound import ASCIISoundSystem
from .ui.hud import GameHUD

# Mock classes for systems not yet implemented
class MultiplayerManager:
    def connect(self): pass
    def sync_state(self): pass
    def disconnect(self): pass

class UltimateCliDoom:
    def __init__(self, width=80, height=25, dev_mode=False, multiplayer=False):
        self.width = width
        self.height = height
        self.dev_mode = dev_mode
        self.multiplayer_enabled = multiplayer

        # Initialize systems
        self.engine = RaycastingEngine(width, height)
        self.world_gen = ProceduralWorldGenerator()
        self.enemy_ai = SimpleEnemyAI()
        self.sound = ASCIISoundSystem()
        self.hud = GameHUD(width, height)

        if multiplayer:
            self.multiplayer = MultiplayerManager()

        # Game state
        self.running = True
        self.paused = False
        self.current_level = 1
        self.tick = 0

    def run(self):
        """Main game loop"""
        self.initialize()

        while self.running:
            self.update()
            self.render()
            self.handle_input()

        self.cleanup()

    def initialize(self):
        """Initialize game systems"""
        print("🌌 Generating quantum world...")
        self.world = self.world_gen.generate_level(self.current_level)

        print("🤖 Spawning enemies...")
        self.enemies = self.enemy_ai.spawn_enemies(self.world, count=5)

        print("🔊 Initializing sound...")
        self.sound.initialize()

        if self.multiplayer_enabled:
            print("🌐 Connecting to network...")
            self.multiplayer.connect()

    def update(self):
        """Update game logic"""
        if self.paused:
            return
        self.tick += 1

        # Update enemies
        self.enemy_ai.update(self.enemies, self.engine.player)

        # Periodic events (e.g., passive score gain)
        if self.tick % 100 == 0:
            self.engine.player.score += 1

        # Update multiplayer state
        if self.multiplayer_enabled:
            self.multiplayer.sync_state()

    def render(self):
        """Render frame"""
        self.engine.clear_screen()

        # Render 3D world + enemies
        frame = self.engine.render_3d(self.world, self.enemies)

        # Add HUD
        frame = self.hud.add_overlay(frame, {
            'level': self.current_level,
            'health': self.engine.player.health,
            'ammo': self.engine.player.ammo,
            'score': self.engine.player.score
        })

        for line in frame:
            print(line)

    def handle_input(self):
        """Handle user input"""
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
                if self.engine.player_shoot(self.enemies):
                    self.sound.play_shoot()
            elif key == 'h':
                # quick heal for demo pacing
                self.engine.player.heal(10)
            elif key == 'e':
                # emulate damage to feel tension
                self.engine.player.take_damage(10)
        except KeyboardInterrupt:
            self.quit_game()
        except:
            pass

    def quit_game(self):
        """Quit game safely"""
        print("🕉️ Saving quantum state...")
        self.running = False

    def toggle_pause(self):
        """Toggle pause"""
        self.paused = not self.paused
        status = "PAUSED" if self.paused else "RESUMED"
        print(f"⏸️ Game {status}")

    def show_map(self):
        """Show ASCII map"""
        map_view = self.world.generate_ascii_map()
        print("\n📍 QUANTUM MAP:")
        for line in map_view:
            print(line)
        input("Press Enter to continue...")

    def cleanup(self):
        """Cleanup resources"""
        if self.multiplayer_enabled:
            self.multiplayer.disconnect()
        print("🌌 Quantum reality collapsed. OM TAT SAT.")
