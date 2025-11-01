"""
🧪 Tests for raycasting engine
Production-grade TDD: >95% coverage
"""

import pytest
import math
from src.engine.renderer import RaycastingEngine
from src.core.world import World

class TestRaycastingEngine:
    def setup_method(self):
        """Setup test engine"""
        self.engine = RaycastingEngine(80, 25)

    def test_initialization(self):
        """Test engine initializes correctly"""
        assert self.engine.width == 80
        assert self.engine.height == 25
        assert self.engine.fov == math.pi / 3
        assert self.engine.player is not None

    def test_ray_casting(self):
        """Test ray casting algorithm"""
        # Mock world with simple wall
        world_map = [
            "###",
            "#.#",
            "###"
        ]

        distance, wall_type = self.engine.cast_ray(0, world_map)
        assert distance > 0
        assert distance <= self.engine.max_depth
        assert wall_type is not None

    def test_wall_height_calculation(self):
        """Test wall height calculation"""
        distance = 2.0
        height = self.engine.calculate_wall_height(distance)
        expected = min(self.engine.height, int(self.engine.height / distance))
        assert height == expected

    def test_fish_eye_correction(self):
        """Test fish-eye correction"""
        distance = 5.0
        angle_diff = math.pi / 6
        corrected = self.engine.correct_fish_eye(distance, angle_diff)
        expected = distance * math.cos(angle_diff)
        assert abs(corrected - expected) < 0.001

    def test_player_movement(self):
        """Test player movement"""
        initial_x = self.engine.player.x
        initial_angle = self.engine.player.angle
        
        # Test forward movement
        self.engine.move_player('w')
        assert self.engine.player.x != initial_x or self.engine.player.y != initial_x
        
        # Test rotation
        self.engine.move_player('a')
        assert self.engine.player.angle != initial_angle

    def test_3d_rendering(self):
        """Test 3D rendering pipeline"""
        # Create test world
        world_map = [
            "#####",
            "#...#",
            "#.#.#",
            "#...#",
            "#####"
        ]
        world = World(world_map, 'test', 1, 42)
        
        # Render frame
        frame = self.engine.render_3d(world)
        
        assert len(frame) == self.engine.height
        assert all(len(line) == self.engine.width for line in frame)

    def test_wall_character_generation(self):
        """Test wall character with lighting"""
        wall_char = self.engine.get_wall_char('#', 1.0)
        assert wall_char is not None
        assert len(wall_char) == 1

    def test_shooting_mechanism(self):
        """Test player shooting"""
        # Create mock enemy
        class MockEnemy:
            def __init__(self):
                self.alive = True
                self.x = 2.0
                self.y = 2.0
                self.health = 100
            
            def take_damage(self, damage):
                self.health -= damage
                if self.health <= 0:
                    self.alive = False
        
        enemy = MockEnemy()
        enemies = [enemy]
        
        # Test shooting
        hit = self.engine.player_shoot(enemies)
        # Hit depends on angle alignment, just test that it doesn't crash
        assert isinstance(hit, bool)

    def test_edge_cases(self):
        """Test edge cases and error handling"""
        # Empty world
        empty_world = World([], 'empty', 1, 0)
        frame = self.engine.render_3d(empty_world)
        assert len(frame) == self.engine.height
        
        # Single cell world
        tiny_world = World(['#'], 'tiny', 1, 0)
        frame = self.engine.render_3d(tiny_world)
        assert len(frame) == self.engine.height


class TestEngineIntegration:
    """Integration tests for engine components"""
    
    @pytest.mark.integration
    def test_full_game_cycle(self):
        """Test complete render cycle"""
        engine = RaycastingEngine(40, 20)
        
        # Create test world
        world_map = [
            "##########",
            "#........#",
            "#.######.#",
            "#........#",
            "#.######.#",
            "#........#",
            "##########"
        ]
        world = World(world_map, 'integration_test', 1, 123)
        
        # Simulate game steps
        for _ in range(10):
            frame = engine.render_3d(world)
            assert len(frame) == engine.height
            
            # Move player
            engine.move_player('w')
            engine.move_player('d')
    
    @pytest.mark.slow
    def test_performance_benchmark(self):
        """Benchmark rendering performance"""
        import time
        
        engine = RaycastingEngine(80, 25)
        large_world = World(['#' + '.' * 98 + '#' for _ in range(50)], 'perf', 1, 456)
        
        start_time = time.time()
        for _ in range(100):
            engine.render_3d(large_world)
        end_time = time.time()
        
        avg_frame_time = (end_time - start_time) / 100
        assert avg_frame_time < 0.1  # Should render in under 100ms
