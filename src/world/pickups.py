"""
Pickups (health/ammo/keycard) and spawn hooks
"""

import random
from typing import List, Tuple

WALKABLE = {'.', '·', '~', ' '}

class Pickup:
    def __init__(self, kind: str, x: float, y: float, amount: int = 0):
        self.kind = kind  # 'health' | 'ammo' | 'keycard'
        self.x = x
        self.y = y
        self.amount = amount
        self.taken = False

    def symbol(self) -> str:
        return {'health': '+', 'ammo': '∎', 'keycard': '⌘'}.get(self.kind, '*')


def spawn_pickups(world_map: List[str], count_rules: dict) -> List[Pickup]:
    spots: List[Tuple[int, int]] = []
    for y, row in enumerate(world_map):
        for x, ch in enumerate(row):
            if ch in WALKABLE:
                spots.append((x, y))
    random.shuffle(spots)

    pickups: List[Pickup] = []
    # Chances / amounts
    hp_ch = float(count_rules.get('health_pack_chance', 0.08))
    am_ch = float(count_rules.get('ammo_pack_chance', 0.10))
    kc_ch = float(count_rules.get('keycard_chance', 0.03))

    budget = min(len(spots), int(len(world_map) * 0.2))
    i = 0
    while i < budget and spots:
        x, y = spots.pop()
        r = random.random()
        if r < kc_ch:
            pickups.append(Pickup('keycard', x + 0.5, y + 0.5))
        elif r < kc_ch + hp_ch:
            pickups.append(Pickup('health', x + 0.5, y + 0.5, amount=20))
        elif r < kc_ch + hp_ch + am_ch:
            pickups.append(Pickup('ammo', x + 0.5, y + 0.5, amount=15))
        i += 1

    return pickups
