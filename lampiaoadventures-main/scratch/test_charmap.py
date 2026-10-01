"""
Verification test for TileSet slicing and ASCII Charmap Level Building.
"""

import os
import pygame

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import sys
sys.path.insert(0, os.path.abspath("."))

from src.level.tilemap import TileSet, TileMapLoader
from src.level.level_manager import LevelManager

def test_tileset_and_charmap():
    print("[Test] Initializing Pygame...")
    pygame.init()
    pygame.display.set_mode((1, 1))

    # Test 1: TileSet Slicing (tilechao1.png)
    tileset = TileSet("assets/sprites/tileset/tilechao1.png", tile_width=32, tile_height=32)
    assert len(tileset.tiles) == 54, f"Expected 54 tiles, got {len(tileset.tiles)}"
    print(f"[Test] TileSet sliced successfully: {tileset.cols} cols x {tileset.rows} rows = {len(tileset.tiles)} tiles.")

    # Test 2: Custom Charmap Parsing
    custom_map = [
        "....P..................",
        "....L#######R...(====).",
        "....[DDDDDDDR..........",
        "....<_______>.........."
    ]
    data = TileMapLoader.parse_charmap(custom_map, tileset, tile_size=32)
    assert len(data['solid_tiles']) == 33, f"Expected 33 solid tiles, got {len(data['solid_tiles'])}"
    assert data['player_spawn'] == (128, 0), f"Player spawn mismatch: {data['player_spawn']}"
    print("[Test] Custom charmap parsed cleanly!")

    # Test 3: LevelManager Charmap Integration
    level_mgr = LevelManager()
    assert len(level_mgr.solid_tiles) > 0, "LevelManager should contain solid tiles!"
    assert level_mgr.solid_tiles[0].surface.get_size() == (32, 32), f"Tile size should be (32, 32), got {level_mgr.solid_tiles[0].surface.get_size()}"
    print("[Test] LevelManager Level 1 built with 32x32 pixel art charmap!")

    print("[Test] SUCCESS: Charmap and Tileset test completed without errors!")

if __name__ == "__main__":
    test_tileset_and_charmap()
