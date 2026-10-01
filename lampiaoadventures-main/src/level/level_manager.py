"""
Level Manager.
Loads level geometry, hazards, collectibles, background props, enemies, NPCs,
and handles player-level collision logic across a 6000px wide stage built using ASCII Charmap and pixel art tilesets.
"""

import pygame
from config import LEVEL_WIDTH, LEVEL_HEIGHT, TILE_SIZE, COLOR_SUN, COLOR_SKY
from src.level.tile import Tile
from src.level.tilemap import TileSet, TileMapLoader
from src.entities.enemy import ChaserEnemy, TanajuraEnemy
from src.entities.npc import NPC
from src.entities.vaca_mojada import VacaMojada
from src.entities.urubu_do_pix import UrubuDoPix
from src.entities.catita import Catita
from src.core.audio_manager import AudioManager

ROW_LEN = 240
r_sky = '.' * ROW_LEN
r14 = '........' + '.' * (ROW_LEN - 9)

r15 = r_sky
r16 = r_sky
r15 = '........................................L####R.............................L######R.............................L####R........................................L######R....................................L####R'.ljust(ROW_LEN, '.')
r17 = '...P........1.........E........2....t............................B....b.....t............................4..........V........t....E..............5.......t.....Z.............1.......t......E..................................F.'.ljust(ROW_LEN, '.')
g1_top = 'L' + '#' * 40 + 'R'
g2_top = 'L' + '#' * 43 + 'R'
g3_top = 'L' + '#' * 43 + 'R'
g4_top = 'L' + '#' * 43 + 'R'
g5_top = 'L' + '#' * 49 + 'R'
r18 = g1_top + '...' + g2_top + '...' + g3_top + '...' + g4_top + '...' + g5_top

g1_dirt = '[' + 'D' * 40 + ']'
g2_dirt = '[' + 'D' * 43 + ']'
g3_dirt = '[' + 'D' * 43 + ']'
g4_dirt = '[' + 'D' * 43 + ']'
g5_dirt = '[' + 'D' * 49 + ']'
r_dirt = g1_dirt + '...' + g2_dirt + '...' + g3_dirt + '...' + g4_dirt + '...' + g5_dirt

g1_bot = '<' + '_' * 40 + '>'
g2_bot = '<' + '_' * 43 + '>'
g3_bot = '<' + '_' * 43 + '>'
g4_bot = '<' + '_' * 43 + '>'
g5_bot = '<' + '_' * 49 + '>'
r22 = g1_bot + '...' + g2_bot + '...' + g3_bot + '...' + g4_bot + '...' + g5_bot

LEVEL_1_CHARMAP = [r_sky]*14 + [r14, r15, r16, r17, r18, r_dirt, r_dirt, r_dirt, r22]

class LevelManager:
    def __init__(self):
        self.tiles = []
        self.solid_tiles = []
        self.hazards = []
        self.collectibles = []
        self.props = []
        self.enemies = []
        self.npcs = []
        self.vaca_mojada = None
        self.urubu_do_pix = None
        self.catita = None
        
        self.level_width = LEVEL_WIDTH
        self.level_height = LEVEL_HEIGHT
        self.player_spawn = (100, 520)
        self.level_completed = False
        self.finish_trigger = pygame.Rect(7200, 480, 100, 160)

        self.audio_manager = AudioManager()
        self.tileset = None
        self.load_level_1()

    def load_level_1(self):
        """Generates Level 1 using 32x32 pixel art charmap layout with tilechao1.png tileset."""
        self.tiles.clear()
        self.solid_tiles.clear()
        self.hazards.clear()
        self.collectibles.clear()
        self.props.clear()
        self.enemies.clear()
        self.npcs.clear()
        self.vaca_mojada = None
        self.urubu_do_pix = UrubuDoPix()

        # Load tileset (tilechao1.png - 32x32 pixel art tiles)
        self.tileset = TileSet("assets/sprites/tileset/tilechao1.png", tile_width=32, tile_height=32)

        # Parse ASCII Charmap grid layout
        level_data = TileMapLoader.parse_charmap(LEVEL_1_CHARMAP, self.tileset, tile_size=32)

        self.solid_tiles = level_data['solid_tiles']
        self.tiles = list(self.solid_tiles)
        self.hazards = level_data['hazards']
        self.collectibles = level_data['collectibles']
        self.props = level_data['props']
        self.npcs = level_data['npcs']
        self.enemies = level_data['enemies']
        self.vaca_mojada = level_data.get('vaca_mojada') or VacaMojada(x=3776, y=512, trigger_x=3600)
        self.player_spawn = level_data['player_spawn']
        self.finish_trigger = level_data['finish_trigger']
        self.level_width = level_data['level_width']
        self.level_height = level_data['level_height']
        self.catita = Catita(x=self.finish_trigger.x + 20, y=544)

        # Populate enemies along ground stretches and platforms
        enemy_spawns = [
            (850, 512, 140),
            (1600, 512, 180),
            (2500, 512, 160),
            (3200, 512, 200),
            (4100, 512, 180),
            (5300, 512, 220),
            (6200, 512, 180),
            (6700, 512, 160)
        ]
        for ex, ey, patrol_dist in enemy_spawns:
            self.enemies.append(ChaserEnemy(x=ex, y=ey, patrol_dist=patrol_dist))

        hazard_locations = [
            (600, 544), (900, 544),
            (2780, 544), (2600, 544),
            (4220, 544), (2680, 544),
            (5660, 544), (6000, 544)
        ]

        for hx, hy in hazard_locations:
            self.hazards.append(Tile(hx, hy, 32, 32, Tile.TYPE_HAZARD, label="CACTUS"))


        # Add flying Tanajuras
        tanajura_spawns = [
            (450, 512, 100),
            (1250, 512, 120),
            (2150, 512, 100),
            (3550, 512, 150),
            (4850, 512, 120),
            (5950, 512, 130),
            (6550, 512, 100)
        ]
        for tx, ty, patrol_dist in tanajura_spawns:
            self.enemies.append(TanajuraEnemy(x=tx, y=ty, patrol_dist=patrol_dist))

        # Clear all hazards/cacti and catita coins as requested
        self.hazards.clear()
        self.collectibles.clear()

    def load_custom_charmap(self, charmap_lines: list, tileset_path: str = "assets/sprites/tileset/tilechao1.png", charmap_dict: dict = None, tile_size: int = 32):
        """Allows loading any custom charmap layout and tileset file on the fly."""
        self.tiles.clear()
        self.solid_tiles.clear()
        self.hazards.clear()
        self.collectibles.clear()
        self.props.clear()
        self.enemies.clear()
        self.npcs.clear()
        self.vaca_mojada = None

        self.tileset = TileSet(tileset_path, tile_width=tile_size, tile_height=tile_size)
        level_data = TileMapLoader.parse_charmap(charmap_lines, self.tileset, charmap_dict=charmap_dict, tile_size=tile_size)

        self.solid_tiles = level_data['solid_tiles']
        self.tiles = list(self.solid_tiles)
        self.hazards = level_data['hazards']
        self.collectibles = level_data['collectibles']
        self.props = level_data['props']
        self.npcs = level_data['npcs']
        self.enemies = level_data['enemies']
        self.vaca_mojada = level_data.get('vaca_mojada')
        self.urubu_do_pix = UrubuDoPix()
        self.player_spawn = level_data['player_spawn']
        self.finish_trigger = level_data['finish_trigger']
        self.level_width = level_data['level_width']
        self.level_height = level_data['level_height']

    def update(self, dt: float, player, camera=None):
        """Update tiles, props, enemies, Vaca Mojada, and check collisions with player."""
        for prop in self.props:
            prop.update(dt)

        for coin in self.collectibles:
            coin.update(dt)

        is_praying = any(getattr(npc, 'anim_state', '') == 'PRAY' for npc in self.npcs)

        for npc in self.npcs:
            npc.update(dt, self.solid_tiles, player)

        for enemy in self.enemies:
            if enemy.is_active:
                if not is_praying:
                    enemy.update_ai(dt, player, self.solid_tiles)
                    if enemy.get_hitbox().colliderect(player.get_hitbox()):
                        player.take_damage(enemy.damage)

        if self.vaca_mojada:
            self.vaca_mojada.update_boss(dt, player, camera, self.solid_tiles)

        if self.urubu_do_pix and self.urubu_do_pix.is_active:
            self.urubu_do_pix.update(dt, player, camera, self.level_width)

        if self.catita:
            self.catita.update(dt)

        for hazard in self.hazards:
            if hazard.rect.colliderect(player.get_hitbox()):
                player.take_damage(35)

        # Respawn if player falls into pit/abyss
        if player.pos.y > self.level_height - 60 or player.pos.y > 660:
            player.pos = pygame.Vector2(self.player_spawn[0], self.player_spawn[1])
            player.vel = pygame.Vector2(0, 0)

        for coin in self.collectibles:
            if coin.is_active and coin.rect.colliderect(player.get_hitbox()):
                coin.is_active = False
                player.coins_collected += 1
                self.audio_manager.play_sfx("assets/audio/sfx/coin.wav")

        # Level completion is triggered by interacting with Catita at the end of the stage ([E] key)
        pass

    def render(self, screen: pygame.Surface, camera):
        """Renders parallax background elements, props, tiles, hazards, collectibles, NPCs, enemies, and Vaca Mojada."""
        for prop in self.props:
            prop.render(screen, camera)

        for tile in self.solid_tiles:
            tile.render(screen, camera)

        for hazard in self.hazards:
            hazard.render(screen, camera)

        for coin in self.collectibles:
            if coin.is_active:
                coin.render(screen, camera)

        for npc in self.npcs:
            npc.render(screen, camera)

        for enemy in self.enemies:
            if enemy.is_active:
                enemy.render(screen, camera)

        if self.vaca_mojada:
            self.vaca_mojada.render(screen, camera)

        if self.urubu_do_pix and self.urubu_do_pix.is_active:
            self.urubu_do_pix.render(screen, camera)

        if self.catita:
            self.catita.render(screen, camera)

