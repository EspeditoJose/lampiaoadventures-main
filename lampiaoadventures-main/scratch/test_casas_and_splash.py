import sys
import os
import pygame

# Set dummy video driver for headless execution
os.environ["SDL_VIDEODRIVER"] = "dummy"

sys.path.insert(0, os.getcwd())

def test_casas_and_splash():
    pygame.init()
    pygame.display.set_mode((800, 600))

    from src.level.level_manager import LevelManager
    from src.ui.splash_transition import SplashTransition
    from src.scenes.level_scene import LevelScene

    print("--- 1. Testing Houses Distribution & Charmap Parsing ---")
    lm = LevelManager()
    house_props = [p for p in lm.props if "CASA" in p.label]
    assert len(house_props) > 0, "Expected house props to be loaded from charmap!"
    print(f"[PASS] Successfully loaded {len(house_props)} house props distributed across stage!")
    for h in house_props[:3]:
        print(f"  - House: {h.label} at pos ({h.rect.x}, {h.rect.y}) size ({h.rect.width}x{h.rect.height})")

    print("\n--- 2. Testing Splash Transition (Produced By Fade-In -> Hold -> Fade-Out) ---")
    splash = SplashTransition()
    assert not splash.is_active(), "Splash should be inactive initially"

    completed = [False]
    def on_done():
        completed[0] = True

    splash.trigger(on_complete=on_done)
    assert splash.is_active(), "Splash should be active after trigger()"

    # Fade in phase (1.0s)
    splash.update(0.5)
    assert splash.state == SplashTransition.STATE_FADE_IN, f"Expected FADE_IN, got {splash.state}"
    assert 0 < splash.alpha < 255, f"Expected intermediate alpha, got {splash.alpha}"

    splash.update(0.6)
    assert splash.state == SplashTransition.STATE_HOLD, f"Expected HOLD state, got {splash.state}"
    assert splash.alpha == 255.0, f"Expected max alpha (255), got {splash.alpha}"

    # Hold phase (1.2s) -> transition to Fade Out
    splash.update(1.3)
    assert splash.state == SplashTransition.STATE_FADE_OUT, f"Expected FADE_OUT, got {splash.state}"

    # Fade out phase (1.0s) -> transition to Inactive & trigger callback
    splash.update(1.1)
    assert not splash.is_active(), "Splash should be inactive after full cycle"
    assert completed[0] == True, "Expected on_complete callback to be called!"
    print("[PASS] SplashTransition completed fade-in, hold, fade-out cycle cleanly!")

    print("\n--- 3. Testing LevelScene Game Start & Jegue Dialogue Splash Triggers ---")
    scene = LevelScene()
    scene.on_enter()
    assert scene.splash.is_active(), "LevelScene should trigger Produced By splash transition on game start!"

    # Complete splash intro cycle
    scene.splash.update(3.5)
    assert not scene.splash.is_active(), "Splash intro should complete"

    # Find Jegue NPC
    jegue_npc = next((n for n in scene.level_manager.npcs if "jegue" in n.name.lower() or n.label == "JEGUE"), None)
    assert jegue_npc is not None, "Jegue NPC should exist at the start of Level 1!"
    print(f"[PASS] Found NPC: {jegue_npc.name} ({jegue_npc.label})")

    # Simulate Jegue dialogue completion
    scene.player.pos.x = jegue_npc.pos.x
    scene.player.interact_pressed = True
    scene.update(0.016)  # Opens dialogue box
    assert scene.dialogue_box.is_active, "Dialogue box should be open"

    # Close dialogue box by stepping through pages
    for _ in range(len(jegue_npc.dialogue_pages)):
        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN)
        scene.dialogue_box.handle_events([event])

    scene.update(0.016)
    assert scene.splash.is_active(), "Completing Jegue dialogue should trigger Produced By splash transition!"
    print("[PASS] Produced By splash transition triggered after completing Jegue dialogue!")

    print("\nALL CASAS, CHARMAP, AND SPLASH TRANSITION TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    test_casas_and_splash()
