import os
import pygame

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

pygame.init()
pygame.display.set_mode((640, 360))

from src.level.level_manager import LevelManager

lm = LevelManager()

print("Level width:", lm.level_width)
print("Level height:", lm.level_height)
print("Solid tiles count:", len(lm.solid_tiles))
print("Enemies count:", len(lm.enemies))
print("Hazards count:", len(lm.hazards))
print("Props count:", len(lm.props))
print("Catita pos:", (lm.catita.pos.x, lm.catita.pos.y) if lm.catita else None)

# Verify no untextured dummy placeholder props exist
for prop in lm.props:
    label = getattr(prop, 'label', '')
    print(f"Prop label: {label}, pos: ({prop.rect.x}, {prop.rect.y})")
    assert label != "JUMENTO_VOADOR", "Placeholder box prop JUMENTO_VOADOR must be removed!"

assert lm.level_width == 7680, f"Expected 7680px level width, got {lm.level_width}"
assert len(lm.enemies) >= 15, f"Expected at least 15 enemies, got {len(lm.enemies)}"
assert lm.catita is not None, "Catita must be placed at the end of the stage!"

print("Expanded concise map test passed 100% successfully!")
