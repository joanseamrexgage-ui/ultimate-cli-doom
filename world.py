"""
🗺️ WORLD CLASS - Represents game world state
"""

from typing import List, Tuple, Optional

class World:
    def __init__(self, world_map: List[str], theme: str, level: int, seed: int):
        self.map = world_map
        self.theme = theme
        self.level = level
        self.seed = seed
        self.width = len(world_map[0]) if world_map else 0
        self.height = len(world_map)

        # Special elements tracking
        self.special_elements = self.find_special_elements()
        self.pickups = []
        self.secrets = []

    def find_special_elements(self) -> List[Tuple[int, int, str]]:
        """Find all special elements in the map"""
        elements = []
        special_chars = ['Q', 'A', 'L', 'B', '🕉']

        for y, row in enumerate(self.map):
            for x, char in enumerate(row):
                if char in special_chars:
                    elements.append((x, y, char))

        return elements

    def is_walkable(self, x: int, y: int) -> bool:
        """Check if position is walkable"""
        if (x < 0 or x >= self.width or y < 0 or y >= self.height):
            return False

        walkable_chars = ['.', '·', '~', ' ']
        return self.map[y][x] in walkable_chars

    def get_tile_type(self, x: int, y: int) -> str:
        """Get tile type at position"""
        if (x < 0 or x >= self.width or y < 0 or y >= self.height):
            return 'void'
        return self.map[y][x]

    def activate_special(self, x: int, y: int) -> Optional[str]:
        """Activate special element at position"""
        tile = self.get_tile_type(x, y)

        if tile == 'Q':  # Quantum portal
            return "quantum_teleport"
        elif tile == 'A':  # Atman meditation
            return "atman_heal"
        elif tile == 'L':  # Loqiemean portal
            return "loqiemean_power"
        elif tile == 'B':  # Batut bounce
            return "batut_jump"

        return None

    def generate_ascii_map(self) -> List[str]:
        """Generate ASCII minimap"""
        minimap = ["🗺️  WORLD MAP:"]
        minimap.extend(self.map)
        minimap.append(f"Theme: {self.theme} | Level: {self.level} | Seed: {self.seed}")
        return minimap

    def save_to_file(self, filename: str):
        """Save world to file"""
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"THEME:{self.theme}\n")
            f.write(f"LEVEL:{self.level}\n")
            f.write(f"SEED:{self.seed}\n")
            f.write("MAP:\n")
            for row in self.map:
                f.write(row + "\n")

    @classmethod
    def load_from_file(cls, filename: str) -> 'World':
        """Load world from file"""
        with open(filename, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        theme = lines[0].split(':')[1].strip()
        level = int(lines[1].split(':')[1].strip())
        seed = int(lines[2].split(':')[1].strip())

        world_map = []
        for line in lines[4:]:  # Skip header lines
            if line.strip():
                world_map.append(line.rstrip('\n'))

        return cls(world_map, theme, level, seed)