import os
import pygame

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

pygame.init()
pygame.display.set_mode((640, 360))

from src.entities.enemy import CalangoEnemy
from src.entities.player import Player
from src.level.tile import Tile

# Create ground tiles ending at x = 228 (cliff edge at x = 228)
tiles = [
    Tile(100, 544, 32, 32, Tile.TYPE_SOLID),
    Tile(132, 544, 32, 32, Tile.TYPE_SOLID),
    Tile(164, 544, 32, 32, Tile.TYPE_SOLID),
    Tile(196, 544, 32, 32, Tile.TYPE_SOLID)
]

calango = CalangoEnemy(180.0, 496.0)
player = Player(1000.0, 500.0) # Player is far to the right (outside detection radius)

print("Initial direction:", calango.direction)

# Update AI over 5 frames
for i in range(5):
    calango.update_ai(0.1, player, tiles)

print("Direction after reaching cliff edge:", calango.direction)

# Assert that calango turned around instead of stepping off cliff
assert calango.direction == -1, "Calango must turn around when reaching an abyss cliff edge!"

print("Enemy pit detection & direction flip test passed 100% successfully!")
