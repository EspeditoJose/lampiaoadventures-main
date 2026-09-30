"""
Lampião Adventures: The Busca of The Catita
Main entry point & game loop initializer.
"""

from src.core.engine import Engine
from src.scenes.menu_scene import MenuScene
from src.scenes.level_scene import LevelScene
from src.scenes.cutscene_scene import CutsceneScene

def main():
    engine = Engine()

    # Instantiate scenes
    menu_scene = MenuScene()
    level_scene = LevelScene()
    cutscene_scene = CutsceneScene()

    # Register scenes in SceneManager
    engine.scene_manager.register_scene("MENU", menu_scene)
    engine.scene_manager.register_scene("LEVEL_1", level_scene)
    engine.scene_manager.register_scene("CUTSCENE", cutscene_scene)

    # Start game on Main Menu
    engine.scene_manager.change_scene("MENU")

    # Start main engine loop
    engine.run()

if __name__ == "__main__":
    main()
