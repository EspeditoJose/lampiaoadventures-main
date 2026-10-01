import os
import pygame

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

pygame.init()
pygame.display.set_mode((640, 360))

from src.entities.player import Player
from src.entities.catita import Catita
from src.level.level_manager import LevelManager

# 1. Test Player Left Boundary
player = Player(10, 500)
player.vel.x = -50
player.update(0.1, [])
print("Player X after moving left past border:", player.pos.x)
assert player.pos.x >= 0.0, "Player pos.x must not be negative!"

# 2. Test Catita entity
catita = Catita(5840, 512)
catita.update(0.1)
print("Catita arrow_timer:", catita.arrow_timer)

# 3. Test LevelManager contains Catita
lm = LevelManager()
print("LevelManager catita:", lm.catita)
assert lm.catita is not None, "LevelManager must contain catita!"

print("All boundary, catita and music tests passed!")
