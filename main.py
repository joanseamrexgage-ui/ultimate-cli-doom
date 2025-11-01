#!/usr/bin/env python3
"""
🔥 ULTIMATE CLI DOOM - Main Entry Point
Run: python main.py
"""

import sys
import argparse
from src.game import UltimateCliDoom

def main():
    parser = argparse.ArgumentParser(description="Ultimate CLI DOOM")
    parser.add_argument("--dev", action="store_true", help="Developer mode")
    parser.add_argument("--width", type=int, default=80, help="Screen width")
    parser.add_argument("--height", type=int, default=25, help="Screen height")
    parser.add_argument("--multiplayer", action="store_true", help="Multiplayer mode")
    args = parser.parse_args()

    print("🔥 ULTIMATE CLI DOOM")
    print("Loading quantum reality...")

    game = UltimateCliDoom(
        width=args.width,
        height=args.height,
        dev_mode=args.dev,
        multiplayer=args.multiplayer
    )

    try:
        game.run()
    except KeyboardInterrupt:
        print("\n🕉️ Game interrupted. OM.")
        sys.exit(0)

if __name__ == "__main__":
    main()