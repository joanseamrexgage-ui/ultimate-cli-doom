"""
Wire HUD/engine callbacks; add weapon mode switching and projectile update; handle enemy shooter telegraph
"""

import sys
from .engine.renderer import RaycastingEngine
from .world.generator import ProceduralWorldGenerator
from .ai.enemies import SimpleEnemyAI
from .audio.sound import ASCIISoundSystem
from .ui.hud import GameHUD

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

        self.engine = RaycastingEngine(width, height)
        self.world_gen = ProceduralWorldGenerator()
        self.enemy_ai = SimpleEnemyAI()
        self.sound = ASCIISoundSystem()
        self.hud = GameHUD(width, height)

        # wire feedback callbacks
        self.engine.banner_cb = lambda text: self.hud.notify(text)
        self.engine.flash_cb = lambda: self.hud.damage_flash()

        if multiplayer:
            self.multiplayer = MultiplayerManager()

        self.running = True
        self.paused = False
        self.current_level = 1
        self.tick = 0
        self.weapon_mode = 'pistol'  # 'pistol' | 'shotgun' | 'rocket'

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
        print("🤖 Spawning enemies...")
        self.enemies = self.enemy_ai.spawn_enemies(self.world, count=6)
        print("🔊 Initializing sound...")
        self.sound.initialize()
        if self.multiplayer_enabled:
            print("🌐 Connecting to network...")
            self.multiplayer.connect()

    def update(self):
        if self.paused:
            return
        self.tick += 1
        self.enemy_ai.update(self.enemies, self.engine.player, world=self.world)
        # projectiles
        self.engine.update_projectiles(self.world, self.enemies)
        # pickups
        self.engine.try_pickups(self.world)
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
        })
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
