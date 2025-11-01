#!/usr/bin/env python3
"""
Pytest Configuration and Global Fixtures
Production-grade test setup with comprehensive mocking
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch

# Add src to Python path for testing
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(project_root, 'src'))

# Test configuration
TEST_WIDTH = 40
TEST_HEIGHT = 20
TEST_SEED = 42

@pytest.fixture(scope="session")
def test_config():
    """Global test configuration"""
    return {
        'width': TEST_WIDTH,
        'height': TEST_HEIGHT,
        'seed': TEST_SEED,
        'mock_input': True,
        'dev_mode': True,
        'multiplayer': False
    }

@pytest.fixture(scope="function")
def mock_input():
    """Mock user input for testing"""
    with patch('builtins.input', return_value='q'):
        yield

@pytest.fixture(scope="function")
def mock_print():
    """Mock print for testing output"""
    with patch('builtins.print') as mock_print:
        yield mock_print

@pytest.fixture(scope="function")
def mock_game_systems():
    """Mock all game systems for isolated testing"""
    mocks = {
        'engine': Mock(),
        'world_gen': Mock(),
        'enemy_ai': Mock(),
        'sound': Mock(),
        'hud': Mock(),
        'multiplayer': Mock()
    }
    
    # Configure mock behaviors
    mocks['engine'].render_3d.return_value = ["#" * TEST_WIDTH for _ in range(TEST_HEIGHT)]
    mocks['world_gen'].generate_level.return_value = Mock()
    mocks['enemy_ai'].spawn_enemies.return_value = []
    
    yield mocks

@pytest.fixture(scope="function")
def sample_world():
    """Sample world data for testing"""
    world = {
        'width': TEST_WIDTH,
        'height': TEST_HEIGHT,
        'walls': [[1 if i == 0 or i == TEST_WIDTH-1 or j == 0 or j == TEST_HEIGHT-1 else 0 
                   for i in range(TEST_WIDTH)] for j in range(TEST_HEIGHT)],
        'spawn_points': [(5, 5), (10, 10)],
        'enemies': [],
        'items': []
    }
    return world

@pytest.fixture(scope="function")
def sample_player():
    """Sample player data for testing"""
    return {
        'x': 5.0,
        'y': 5.0,
        'angle': 0.0,
        'health': 100,
        'ammo': 50,
        'score': 0,
        'level': 1
    }

# Test markers for categorization
def pytest_configure(config):
    """Configure custom pytest markers"""
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "unit: mark test as unit test"
    )
    config.addinivalue_line(
        "markers", "ai: mark test as AI/ML component test"
    )
    config.addinivalue_line(
        "markers", "network: mark test as networking test"
    )

# Pytest collection hooks
def pytest_collection_modifyitems(config, items):
    """Modify test collection - add markers based on test location"""
    for item in items:
        # Add unit marker to all tests by default
        if not any(marker.name in ['integration', 'slow', 'ai', 'network'] 
                  for marker in item.iter_markers()):
            item.add_marker(pytest.mark.unit)
        
        # Add slow marker to tests that might be slow
        if 'ai' in item.name.lower() or 'quantum' in item.name.lower():
            item.add_marker(pytest.mark.slow)
            item.add_marker(pytest.mark.ai)
        
        if 'multiplayer' in item.name.lower() or 'network' in item.name.lower():
            item.add_marker(pytest.mark.network)

# Setup and teardown hooks
@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Setup test environment before all tests"""
    # Set test environment variables
    os.environ['TESTING'] = '1'
    os.environ['PYTHONPATH'] = os.pathsep.join([os.getcwd(), os.path.join(os.getcwd(), 'src')])
    
    yield
    
    # Cleanup after all tests
    if 'TESTING' in os.environ:
        del os.environ['TESTING']

@pytest.fixture(scope="function", autouse=True)
def reset_test_state():
    """Reset test state before each test"""
    # Reset any global state here
    yield
    # Cleanup after each test
