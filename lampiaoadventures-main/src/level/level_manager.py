"""
Level Manager.
Loads level geometry, hazards, collectibles, background props, enemies, NPCs,
and handles player-level collision logic across a 6000px wide stage.
"""

import pygame
from config import LEVEL_WIDTH, LEVEL_HEIGHT, TILE_SIZE, COLOR_SUN, COLOR_SKY
from src.level.tile import Tile
from src.entities.enemy import ChaserEnemy
from src.entities.npc import NPC
from src.core.audio_manager import AudioManager

class LevelManager:
    def __init__(self):
        self.tiles = []
        self.solid_tiles = []
        self.hazards = []
        self.collectibles = []
        self.props = []
        self.enemies = []
        self.npcs = []
        
        self.level_width = LEVEL_WIDTH
        self.level_height = LEVEL_HEIGHT
        self.player_spawn = (100, 520)
        self.level_completed = False
        self.finish_trigger = pygame.Rect(5800, 480, 100, 160)

        self.audio_manager = AudioManager()
        self.load_level_1()

    def load_level_1(self):
        """Generates Level 1: 'O Sertão de Canudos' (6000x720 horizontal map)."""
        self.tiles.clear()
        self.solid_tiles.clear()
        self.hazards.clear()
        self.collectibles.clear()
        self.props.clear()
        self.enemies.clear()
        self.npcs.clear()

        # ----------------------------------------------------
        # 1. GENERATE TERRAIN & SOLID PLATFORMS (6000px wide)
        # ----------------------------------------------------
        ground_y = 640
        
        # Ground segments with deliberate gaps / pits for platforming
        ground_segments = [
            (0, 1400),      # Vila initial ground
            (1550, 2600),   # Cactus Canyon ground
            (2750, 4000),   # Serrote ground
            (4200, 6000)    # Final stretch ground
        ]

        for start_x, end_x in ground_segments:
            for x in range(start_x, end_x, TILE_SIZE):
                for y in range(ground_y, LEVEL_HEIGHT, TILE_SIZE):
                    tile = Tile(x, y, TILE_SIZE, TILE_SIZE, Tile.TYPE_SOLID, label="EARTH")
                    self.tiles.append(tile)
                    self.solid_tiles.append(tile)

        # Elevated Wooden Platforms & Stepping Stones
        platforms = [
            # Section 1: Intro platforms
            (400, 500, 4, "WOOD"),
            (700, 420, 3, "WOOD"),
            (1000, 500, 3, "WOOD"),

            # Pit crossing 1 (1400 -> 1550)
            (1420, 530, 2, "STONE"),

            # Section 2: Cactus Canyon platforms
            (1700, 500, 4, "WOOD"),
            (1950, 400, 5, "WOOD"),
            (2300, 480, 4, "WOOD"),

            # Pit crossing 2 (2600 -> 2750)
            (2620, 520, 2, "STONE"),

            # Section 3: High Serrote Platforms
            (2900, 480, 3, "WOOD"),
            (3150, 360, 4, "WOOD"),
            (3450, 460, 3, "STONE"),
            (3700, 340, 5, "WOOD"),

            # Pit crossing 3 (4000 -> 4200)
            (4040, 520, 1, "STONE"),
            (4120, 440, 1, "STONE"),

            # Section 4: Final Challenge Scaffolding
            (4400, 500, 4, "WOOD"),
            (4700, 380, 6, "WOOD"),
            (5100, 480, 4, "WOOD"),
            (5400, 400, 5, "WOOD")
        ]

        for px, py, width_tiles, label in platforms:
            for i in range(width_tiles):
                tile = Tile(px + i * TILE_SIZE, py, TILE_SIZE, TILE_SIZE, Tile.TYPE_SOLID, label=label)
                self.tiles.append(tile)
                self.solid_tiles.append(tile)

        # ----------------------------------------------------
        # 2. HAZARDS (Cacti & Spikes)
        # ----------------------------------------------------
        hazard_locations = [
            (800, 600), (1200, 600), (1800, 600), (2100, 600),
            (3000, 600), (3300, 600), (3800, 600), (4600, 600), (4900, 600)
        ]

        for hx, hy in hazard_locations:
            hazard = Tile(hx, hy, TILE_SIZE, TILE_SIZE, Tile.TYPE_HAZARD, label="CACTUS")
            self.tiles.append(hazard)
            self.hazards.append(hazard)

        # Bottom Pit Boundary Hazard (instant respawn/damage if player falls into abyss)
        for pit_x in range(1400, 1550, TILE_SIZE):
            self.hazards.append(Tile(pit_x, 700, TILE_SIZE, TILE_SIZE, Tile.TYPE_HAZARD, label="ABYSS"))
        for pit_x in range(2600, 2750, TILE_SIZE):
            self.hazards.append(Tile(pit_x, 700, TILE_SIZE, TILE_SIZE, Tile.TYPE_HAZARD, label="ABYSS"))
        for pit_x in range(4000, 4200, TILE_SIZE):
            self.hazards.append(Tile(pit_x, 700, TILE_SIZE, TILE_SIZE, Tile.TYPE_HAZARD, label="ABYSS"))

        # ----------------------------------------------------
        # 3. COLLECTIBLES (Catita Gold Coins)
        # ----------------------------------------------------
        coin_positions = [
            (420, 450), (460, 450), (720, 370), (1020, 450),
            (1720, 450), (1980, 350), (2020, 350), (2320, 430),
            (2920, 430), (3180, 310), (3220, 310), (3720, 290),
            (4420, 450), (4720, 330), (4760, 330), (5120, 430),
            (5420, 350), (5460, 350), (5700, 580)
        ]

        for cx, cy in coin_positions:
            coin = Tile(cx, cy, 28, 28, Tile.TYPE_COLLECTIBLE, label="CATITA")
            self.collectibles.append(coin)

        # ----------------------------------------------------
        # 4. BACKGROUND PROPS & MEME EASTER EGGS
        # ----------------------------------------------------
        # Backland Sun
        self.props.append(Tile(800, 100, 120, 120, Tile.TYPE_PROP, label="SOL_SERTAO"))

        # Windmill animated prop
        self.props.append(Tile(500, 520, 80, 120, Tile.TYPE_PROP, label="MOINHO"))
        
        # Meme easter egg posters / props
        self.props.append(Tile(2200, 560, 60, 80, Tile.TYPE_PROP, label="PRESEPADA"))
        self.props.append(Tile(3600, 260, 80, 80, Tile.TYPE_PROP, label="JUMENTO_VOADOR"))
        self.props.append(Tile(5600, 520, 100, 120, Tile.TYPE_PROP, label="PORTAL_CATITA"))

        # ----------------------------------------------------
        # 5. NPCS
        # ----------------------------------------------------
        npc_ze = NPC(
            x=250, y=584, name="Zé do Chapéu", label="ZE_CHAPEU",
            dialogue_pages=[
                "Ôente, Lampião! A Catita sumiu no sertão!",
                "Cuidado com os cangaceiros que estão pela caatinga!",
                "Segure [SHIFT] para dar um pique, mas cuidado pra não ficar cansado.",
                "Siga em frente até o Portal da Catita Perdida!"
            ]
        )
        npc_padre = NPC(
            x=2800, y=584, name="Padre Cícero", label="PADRE",
            dialogue_pages=[
                "Que a benção do sertão lhe acompanhe, meu filho!",
                "Restaure suas forças e tome cuidado com os cactos no caminho."
            ]
        )
        self.npcs.extend([npc_ze, npc_padre])

        # ----------------------------------------------------
        # 6. ENEMIES (Chaser Enemies)
        # ----------------------------------------------------
        enemy_spawns = [
            (900, 592, 150),
            (1850, 592, 200),
            (2400, 432, 120),
            (3300, 592, 220),
            (3750, 292, 100),
            (4500, 592, 250),
            (5200, 432, 150)
        ]

        for ex, ey, patrol_dist in enemy_spawns:
            enemy = ChaserEnemy(x=ex, y=ey, patrol_dist=patrol_dist)
            self.enemies.append(enemy)

    def update(self, dt: float, player):
        """Update tiles, props, enemies, and check collisions with player."""
        # Update animated props & tiles
        for prop in self.props:
            prop.update(dt)

        for coin in self.collectibles:
            coin.update(dt)

        # Update NPCs
        for npc in self.npcs:
            npc.update(dt, self.solid_tiles)

        # Update Enemies & AI
        for enemy in self.enemies:
            if enemy.is_active:
                enemy.update_ai(dt, player, self.solid_tiles)
                
                # Check collision with player
                if enemy.get_hitbox().colliderect(player.get_hitbox()):
                    player.take_damage(enemy.damage)

        # Check Hazards Collision
        for hazard in self.hazards:
            if hazard.rect.colliderect(player.get_hitbox()):
                player.take_damage(35)
                # If fallen into abyss, respawn player safely
                if player.pos.y > 680:
                    player.pos = pygame.Vector2(self.player_spawn[0], self.player_spawn[1])
                    player.vel = pygame.Vector2(0, 0)

        # Check Collectibles Collision
        for coin in self.collectibles:
            if coin.is_active and coin.rect.colliderect(player.get_hitbox()):
                coin.is_active = False
                player.coins_collected += 1
                self.audio_manager.play_sfx("assets/audio/sfx/coin.wav")

        # Check Finish Trigger
        if self.finish_trigger.colliderect(player.get_hitbox()):
            self.level_completed = True

    def render(self, screen: pygame.Surface, camera):
        """Renders parallax background elements, props, tiles, hazards, collectibles, NPCs, and enemies."""
        # Render background props
        for prop in self.props:
            prop.render(screen, camera)

        # Render solid tiles
        for tile in self.solid_tiles:
            tile.render(screen, camera)

        # Render hazards
        for hazard in self.hazards:
            hazard.render(screen, camera)

        # Render collectibles
        for coin in self.collectibles:
            if coin.is_active:
                coin.render(screen, camera)

        # Render NPCs
        for npc in self.npcs:
            npc.render(screen, camera)

        # Render Enemies
        for enemy in self.enemies:
            if enemy.is_active:
                enemy.render(screen, camera)

        # Render Level Finish Flag Indicator
        flag_screen_rect = camera.apply(self.finish_trigger)
        if screen.get_rect().colliderect(flag_screen_rect):
            pygame.draw.rect(screen, (255, 215, 0), flag_screen_rect, width=3)
            font = pygame.font.SysFont("arial", 14, bold=True)
            txt = font.render("VILA FINAL", True, (255, 215, 0))
            screen.blit(txt, (flag_screen_rect.x + 5, flag_screen_rect.y + 10))
