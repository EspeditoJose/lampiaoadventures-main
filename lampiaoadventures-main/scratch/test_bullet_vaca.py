import os
import pygame

# Set dummy audio and video driver for headless execution
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

pygame.init()
pygame.display.set_mode((640, 360))

from src.entities.player import Player
from src.entities.vaca_mojada import VacaMojada
from src.entities.bullet import Bullet

# Create entities
player = Player(100, 100)
vaca = VacaMojada(200, 100)
vaca.state = VacaMojada.STATE_RUSHING

# Test bullet collision with Vaca Mojada
bullet = Bullet(200, 100, 12.0, 0.0)
bullet.update(0.016, [], [vaca])

print(f"Bullet active: {bullet.is_active}")
print(f"Vaca HP: {vaca.hp}")

# Test player input & shooting update
event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_j) # shoot key (or KEY_SHOOT)
player.facing = "right"
# Simulate pressing shoot key
player.shoot_cooldown_timer = 0
from config import KEY_SHOOT
# Trigger shoot
player.handle_input([pygame.event.Event(pygame.KEYDOWN, key=KEY_SHOOT[0])])
print(f"Player fired bullets count: {len(player.bullets)}")
if player.bullets:
    b = player.bullets[0]
    print(f"Bullet velocity: ({b.vel.x}, {b.vel.y})")
    assert b.vel.y == 0.0, "Bullet must travel strictly horizontally!"
    b.update(0.016, [], [vaca])

print("Test passed successfully!")
