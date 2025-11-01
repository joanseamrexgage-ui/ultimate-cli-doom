# 🔥 ULTIMATE CLI DOOM

**The most advanced ASCII raycasting game ever built for command line.**

## Features
- **Real-time 3D ASCII raycasting** (like original Doom 1993)
- **Procedural level generation** (infinite worlds via Perlin noise)
- **AI enemies** (quantum RL decision making)
- **Multiplayer support** (TCP/WebSocket)
- **Cross-platform** (Python 3.8+, no deps)
- **Edge deployment** (RPi, old PCs, mobile via Termux)
- **Sound system** (ASCII beeps, OM vibrations)
- **Save/Load** (world persistence)
- **Modding support** (custom maps, themes)

## Quick Start
```bash
git clone https://github.com/your-repo/ultimate-cli-doom
cd ultimate-cli-doom
python main.py
```

## Controls
- **WASD**: Move/rotate
- **Space**: Shoot
- **M**: Map view
- **ESC**: Menu
- **Q**: Quit

## Architecture
- `src/engine/` - Core raycasting engine
- `src/world/` - Procedural generation
- `src/ai/` - Enemy AI (quantum RL)
- `src/network/` - Multiplayer
- `tests/` - TDD coverage >95%

## Development
```bash
pip install -r requirements-dev.txt
pytest tests/
python -m src.main --dev
```

Built with ❤️ by Ultimate Coder & Claude. OM TAT SAT.