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

# ABSOLUTE wall material mappings with hyperdimensional properties
ABSOLUTE_MATERIALS = {
    'stone': {
        'symbols': ['▒', '▓', '█'], 
        'base': '▒',
        'dimensional_phase': 0.0,
        'consciousness_resonance': 0.1,
        'dna_compatibility': 0.3,
        'neural_conductivity': 0.0
    },
    'quantum_crystal': {
        'symbols': ['◆', '◇', '◈', '◉', '◊'], 
        'base': '◆',
        'dimensional_phase': 1.0,
        'consciousness_resonance': 1.0,
        'dna_compatibility': 0.8,
        'neural_conductivity': 0.9
    },
    'living_tissue': {
        'symbols': ['♥', '♡', '❤', '§', '♀'], 
        'base': '♥',
        'dimensional_phase': 0.5,
        'consciousness_resonance': 0.9,
        'dna_compatibility': 1.0,
        'neural_conductivity': 1.0
    },
    'void_matter': {
        'symbols': ['∅', '○', '◯', '◦', ' '], 
        'base': '∅',
        'dimensional_phase': -1.0,
        'consciousness_resonance': 0.0,
        'dna_compatibility': 0.0,
        'neural_conductivity': -0.5
    }
}

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
        self.weapon_overlay_enabled = bool(g.get('weapon_overlay', False))  # Pacifist default
        self.camera_shake = bool(g.get('camera_shake', True))
        self.shake_strength = int(g.get('shake_strength', 1))
        self.shake_frames = int(g.get('shake_frames', 3))
        self.muzzle_flash_frames = int(g.get('muzzle_flash_frames', 2))
        self.muzzle_flash_brightness = int(g.get('muzzle_flash_brightness', 2))
        
        # Navigation aids (always enabled)
        self.minimap_enabled = bool(g.get('minimap_enabled', True))
        self.minimap_width = int(g.get('minimap_width', 15))
        self.minimap_height = int(g.get('minimap_height', 8))
        self.materials_enabled = bool(g.get('materials_enabled', True))
        
        # Initialize ALL graphics systems
        self.gfx = NextGenGraphicsFX(self.cfg)
        self.godlike = GodlikeGraphicsFX(self.cfg)
        self.transcendent = TranscendentGraphicsFX(self.cfg)
        self.absolute = AbsoluteGraphicsEngine(self.cfg)
        
        # Enhanced tracking
        self.visited = set()
        self.player_velocity = 0.0
        self.last_player_pos = (0.0, 0.0)
        self.sound_events = []  # For synesthesia
        self.critical_effects_active = False
        self.meditation_time = 0.0
        self.player_actions = []
        self.observer_angle_history = deque(maxlen=10)
        
        self.player = Player(x=1.5, y=1.5, angle=0)
        self.shake_ttl = 0
        self.muzzle_flash_ttl = 0
        self.projectiles = []
        self.banner_cb = None
        self.flash_cb = None
        self.damage_direction_cb = None

    # ... rest of file unchanged ...
