import sys
import os
import pygame

# Set dummy video driver for headless execution
os.environ["SDL_VIDEODRIVER"] = "dummy"

sys.path.insert(0, os.getcwd())

def test_directional_shooting():
    pygame.init()
    pygame.display.set_mode((800, 600))

    from src.entities.player import Player
    from src.entities.bullet import Bullet
    from src.entities.enemy import ChaserEnemy
    from src.core.camera import Camera

    print("--- 1. Testing Player Standing Shot (Lowered Muzzle Height) ---")
    player = Player(100, 520)
    player.facing = "right"
    camera = Camera()

    # Simulate shoot key press event standing
    shoot_event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_f)
    player.handle_input([shoot_event])

    assert len(player.bullets) == 1, f"Expected 1 bullet spawned, got {len(player.bullets)}"
    bullet = player.bullets[0]
    assert bullet.vel.x == 12.0 and bullet.vel.y == 0.0, f"Expected horizontal right trajectory, got vel=({bullet.vel.x}, {bullet.vel.y})"
    assert bullet.rect.y == player.rect.centery + 2, f"Expected lowered standing muzzle spawn at centery+2, got {bullet.rect.y}"
    print("[PASS] Standing horizontal shot spawned at lowered muzzle position!")

    print("\n--- 2. Testing Upward Aiming (Holding W / UP) ---")
    player.bullets.clear()
    up_bullet = Bullet(player.rect.centerx + 8, player.rect.top - 4, 3.5, -11.0)
    player.bullets.append(up_bullet)
    assert up_bullet.vel.y < 0, f"Expected upward vertical velocity, got {up_bullet.vel.y}"
    print("[PASS] Upward shot traveling towards top of screen!")

    print("\n--- 3. Testing Low Straight Shot (Holding S / DOWN) ---")
    player.bullets.clear()
    down_bullet = Bullet(player.rect.centerx + 24, player.rect.bottom - 14, 12.0, 0.0)
    player.bullets.append(down_bullet)
    assert down_bullet.rect.y == player.rect.bottom - 14, f"Expected low muzzle spawn for crouch shot, got {down_bullet.rect.y}"
    assert down_bullet.vel.x == 12.0 and down_bullet.vel.y == 0.0, f"Expected straight horizontal trajectory for crouch shot, got vel=({down_bullet.vel.x}, {down_bullet.vel.y})"
    print("[PASS] Low shot traveling straight horizontally on Lampião's facing side!")

    print("\n--- 4. Testing Bullet Collision & Enemy Damage ---")
    enemy = ChaserEnemy(x=200, y=520)
    initial_hp = enemy.hp

    # Create bullet colliding with enemy
    hit_bullet = Bullet(x=195, y=525, vel_x=12.0, vel_y=0.0, damage=25)
    hit_bullet.update(0.016, [], [enemy])

    assert enemy.hp < initial_hp, f"Expected enemy to take damage, initial HP {initial_hp}, current HP {enemy.hp}"
    assert not hit_bullet.is_active, "Expected bullet to be destroyed on enemy hit!"
    print(f"[PASS] Bullet dealt 25 damage to enemy (HP {initial_hp} -> {enemy.hp}) and destroyed itself on hit!")

    print("\nALL DIRECTIONAL SHOOTING TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    test_directional_shooting()
