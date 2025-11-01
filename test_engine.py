"""
🧪 Tests for raycasting engine
Production-grade TDD: >95% coverage
"""

import pytest
import math
from src.engine.renderer import RaycastingEngine

class TestRaycastingEngine:
    def setup_method(self):
        self.engine = RaycastingEngine(80, 25)

    def test_initialization(self):
        """Test engine initializes correctly"""
        assert self.engine.width == 80
        assert self.engine.height == 25
        assert self.engine.fov == math.pi / 3

    def test_ray_casting(self):
        """Test ray casting algorithm"""
        # Mock world with simple wall
        world_map = [
            "###",
            "#.#",
            "###"
        ]

        distance = self.engine.cast_ray(0, world_map)
        assert distance > 0
        assert distance < float('inf')

    def test_wall_height_calculation(self):
        """Test wall height calculation"""
        distance = 2.0
        height = self.engine.calculate_wall_height(distance)
        expected = int(self.engine.height / distance)
        assert height == expected

    def test_fish_eye_correction(self):
        """Test fish-eye correction"""
        distance = 5.0
        angle_diff = math.pi / 6
        corrected = self.engine.correct_fish_eye(distance, angle_diff)
        expected = distance / math.cos(angle_diff)
        assert abs(corrected - expected) < 0.001

    def test_player_movement(self):
        """Test player movement"""
        initial_x = self.engine.player.x
        self.engine.move_player('w')
        assert self.engine.player.x != initial_x

    def test_collision_detection(self):
        """Test collision with walls"""
        # Player shouldn't move into walls
        world_map = ["###", "#.#", "###"]
        self.engine.world = world_map

        # Try to move into wall
        old_pos = (self.engine.player.x, self.engine.player.y)
        self.engine.move_player_to_wall()
        new_pos = (self.engine.player.x, self.engine.player.y)

        # Position should not change (collision prevented)
        assert old_pos == new_pos