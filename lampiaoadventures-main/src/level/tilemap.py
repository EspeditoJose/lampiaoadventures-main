"""
Tilemap and Charmap Level Builder.
Allows loading tilesets, slicing them into 32x32 (or custom) pixel art tiles,
and parsing multi-line ASCII charmaps to easily create custom game levels.
"""

import os
import pygame
from src.level.tile import Tile
from src.entities.npc import NPC
from src.entities.enemy import ChaserEnemy, TanajuraEnemy
from src.entities.vaca_mojada import VacaMojada

class TileSet:
    """
    Loads a tileset image and slices it into uniform tile_width x tile_height sub-surfaces.
    """
    def __init__(self, relative_path: str = "assets/sprites/tileset/tilechao1.png", tile_width: int = 32, tile_height: int = 32, colorkey: tuple = None):
        self.relative_path = relative_path
        self.tile_width = tile_width
        self.tile_height = tile_height
        self.colorkey = colorkey
        self.tiles = []
        self.cols = 0
        self.rows = 0

        self.load_and_slice()

    def load_and_slice(self):
        self.tiles.clear()
        full_path = os.path.join(os.getcwd(), self.relative_path)
        
        if not os.path.exists(full_path) or not os.path.isfile(full_path):
            print(f"[TileSet] Warning: Tileset file not found: {full_path}")
            return

        try:
            sheet = pygame.image.load(full_path)
            if pygame.display.get_surface() is not None:
                try:
                    sheet = sheet.convert_alpha()
                except Exception:
                    pass

            sheet_w, sheet_h = sheet.get_size()
            self.cols = sheet_w // self.tile_width
            self.rows = sheet_h // self.tile_height

            for r in range(self.rows):
                for c in range(self.cols):
                    rect = pygame.Rect(c * self.tile_width, r * self.tile_height, self.tile_width, self.tile_height)
                    tile_surf = pygame.Surface((self.tile_width, self.tile_height), pygame.SRCALPHA)
                    tile_surf.blit(sheet, (0, 0), rect)

                    if self.colorkey is not None:
                        tile_surf.set_colorkey(self.colorkey)

                    self.tiles.append(tile_surf)

        except Exception as e:
            print(f"[TileSet] Error loading tileset {full_path}: {e}")

    def get_tile(self, index: int) -> pygame.Surface:
        """Get sliced tile surface by integer index (0..N-1)."""
        if 0 <= index < len(self.tiles):
            return self.tiles[index]
        return None

    def get_tile_by_grid(self, row: int, col: int) -> pygame.Surface:
        """Get sliced tile surface by grid row and column."""
        idx = row * self.cols + col
        return self.get_tile(idx)

    def __getitem__(self, item):
        if isinstance(item, tuple):
            return self.get_tile_by_grid(item[0], item[1])
        return self.get_tile(item)


class TileMapLoader:
    """
    Parses ASCII charmaps to generate level geometry, solid tiles, hazards, collectibles,
    spawns, NPCs, enemies, and boss hazards.
    """

    # Default charmap mapping for tilechao1.png (288x192, 32x32 tiles, 9 cols x 6 rows)
    DEFAULT_CHARMAP = {
        # --- Top Ground Surface ---
        'L': {'type': Tile.TYPE_SOLID, 'tile_idx': 0, 'label': 'GRASS_L'},   # Top-left ground corner
        '#': {'type': Tile.TYPE_SOLID, 'tile_idx': 1, 'label': 'GRASS_M'},   # Top-center ground surface
        'R': {'type': Tile.TYPE_SOLID, 'tile_idx': 2, 'label': 'GRASS_R'},   # Top-right ground corner
        'T': {'type': Tile.TYPE_SOLID, 'tile_idx': 3, 'label': 'GRASS_V'},   # Top ground variant

        # --- Dirt Fill & Side Walls ---
        '[': {'type': Tile.TYPE_SOLID, 'tile_idx': 9, 'label': 'DIRT_L'},    # Left dirt wall
        'D': {'type': Tile.TYPE_SOLID, 'tile_idx': 10, 'label': 'DIRT_M'},   # Center dirt fill
        ']': {'type': Tile.TYPE_SOLID, 'tile_idx': 11, 'label': 'DIRT_R'},   # Right dirt wall
        'd': {'type': Tile.TYPE_SOLID, 'tile_idx': 15, 'label': 'DIRT_V'},   # Center dirt variant

        # --- Bottom Dirt Boundaries ---
        '<': {'type': Tile.TYPE_SOLID, 'tile_idx': 18, 'label': 'DIRT_BL'},  # Bottom-left dirt corner
        '_': {'type': Tile.TYPE_SOLID, 'tile_idx': 19, 'label': 'DIRT_BM'},  # Bottom-center dirt edge
        '>': {'type': Tile.TYPE_SOLID, 'tile_idx': 20, 'label': 'DIRT_BR'},  # Bottom-right dirt corner
        'U': {'type': Tile.TYPE_SOLID, 'tile_idx': 24, 'label': 'UNDERGROUND'}, # Deep underground

        # --- Floating Platforms ---
        '(': {'type': Tile.TYPE_SOLID, 'tile_idx': 4, 'label': 'PLAT_L'},   # Platform left edge
        '=': {'type': Tile.TYPE_SOLID, 'tile_idx': 6, 'label': 'PLAT_M'},   # Platform center
        ')': {'type': Tile.TYPE_SOLID, 'tile_idx': 5, 'label': 'PLAT_R'},   # Platform right edge
        'o': {'type': Tile.TYPE_SOLID, 'tile_idx': 7, 'label': 'PLAT_SOLO'},# Single floating platform block

        # --- Hazards, Collectibles, Props ---
        'X': {'type': Tile.TYPE_HAZARD, 'label': 'CACTUS', 'sprite_path': 'assets/sprites/cacto.png', 'width': 48, 'height': 48},
        'C': {'type': Tile.TYPE_COLLECTIBLE, 'label': 'CATITA'},
        'S': {'type': Tile.TYPE_PROP, 'label': 'SOL_SERTAO'},
        'M': {'type': Tile.TYPE_PROP, 'label': 'MOINHO'},

        # --- House Props ---
        '1': {'type': Tile.TYPE_PROP, 'label': 'CASA_1', 'sprite_path': 'assets/sprites/casas/casa1.png', 'width': 128, 'height': 128},
        '2': {'type': Tile.TYPE_PROP, 'label': 'CASA_2', 'sprite_path': 'assets/sprites/casas/casa2.png', 'width': 128, 'height': 128},
        '3': {'type': Tile.TYPE_PROP, 'label': 'CASA_3', 'sprite_path': 'assets/sprites/casas/casa3.png', 'width': 128, 'height': 128},
        '4': {'type': Tile.TYPE_PROP, 'label': 'CASA_4', 'sprite_path': 'assets/sprites/casas/casa4.png', 'width': 128, 'height': 128},
        '5': {'type': Tile.TYPE_PROP, 'label': 'CASA_5', 'sprite_path': 'assets/sprites/casas/casa5.png', 'width': 128, 'height': 128},

        # --- Spawns & Triggers ---
        'P': {'type': 'PLAYER_SPAWN'},
        'Z': {'type': 'NPC_ZE'},
        'J': {'type': 'NPC_JEGUE'},
        'B': {'type': 'NPC_BEMZEDOR'},
        'E': {'type': 'ENEMY'},
        't': {'type': 'ENEMY_TANAJURA'},
        'V': {'type': 'VACA_MOJADA'},
        'F': {'type': 'FINISH_TRIGGER'},

        # --- Air / Empty ---
        '.': None,
        ' ': None
    }

    @classmethod
    def parse_charmap(cls, charmap_lines: list, tileset: TileSet = None, charmap_dict: dict = None, tile_size: int = 32) -> dict:
        """
        Parses a list of string rows representing the level layout.
        Returns a dictionary containing solid_tiles, hazards, collectibles, props, npcs, enemies,
        vaca_mojada, player_spawn, finish_trigger, level_width, and level_height.
        """
        if tileset is None:
            tileset = TileSet("assets/sprites/tileset/tilechao1.png", tile_size, tile_size)

        mapping = charmap_dict if charmap_dict is not None else cls.DEFAULT_CHARMAP

        solid_tiles = []
        hazards = []
        collectibles = []
        props = []
        npcs = []
        enemies = []
        vaca_mojada = None

        player_spawn = (100, 400)
        finish_trigger = pygame.Rect(5800, 400, 100, 160)

        num_rows = len(charmap_lines)
        max_cols = max(len(row) for row in charmap_lines) if num_rows > 0 else 0

        level_width = max_cols * tile_size
        level_height = num_rows * tile_size

        for row_idx, row in enumerate(charmap_lines):
            for col_idx, char in enumerate(row):
                if char not in mapping or mapping[char] is None:
                    continue

                spec = mapping[char]
                x = col_idx * tile_size
                y = row_idx * tile_size

                spec_type = spec.get('type', '')

                # 1. Solid Tiles / Floating Platforms / Dirt
                if spec_type == Tile.TYPE_SOLID:
                    surf = None
                    if tileset and 'tile_idx' in spec:
                        surf = tileset.get_tile(spec['tile_idx'])
                    elif tileset and 'grid' in spec:
                        r, c = spec['grid']
                        surf = tileset.get_tile_by_grid(r, c)

                    tile = Tile(
                        x=x, y=y, width=tile_size, height=tile_size,
                        tile_type=Tile.TYPE_SOLID, label=spec.get('label', 'SOLID'),
                        surface=surf
                    )
                    solid_tiles.append(tile)

                # 2. Hazards (Cacti / Spikes)
                elif spec_type == Tile.TYPE_HAZARD:
                    w = spec.get('width', 48)
                    h = spec.get('height', 48)
                    sprite_path = spec.get('sprite_path', 'assets/sprites/cacto.png')
                    y_top = y - (h - tile_size) if h > tile_size else y
                    tile = Tile(
                        x=x, y=y_top, width=w, height=h,
                        tile_type=Tile.TYPE_HAZARD, label=spec.get('label', 'CACTUS'),
                        sprite_path=sprite_path
                    )
                    hazards.append(tile)

                # 3. Collectibles (Coins)
                elif spec_type == Tile.TYPE_COLLECTIBLE:
                    coin = Tile(
                        x=x + 2, y=y + 2, width=28, height=28,
                        tile_type=Tile.TYPE_COLLECTIBLE, label=spec.get('label', 'CATITA')
                    )
                    collectibles.append(coin)

                # 4. Props (Houses, Sun, Windmill)
                elif spec_type == Tile.TYPE_PROP:
                    w = spec.get('width', tile_size)
                    h = spec.get('height', tile_size)
                    sprite_path = spec.get('sprite_path', '')
                    y_top = y - (h - tile_size)
                    prop = Tile(
                        x=x, y=y_top, width=w, height=h,
                        tile_type=Tile.TYPE_PROP, label=spec.get('label', 'PROP'),
                        sprite_path=sprite_path
                    )
                    props.append(prop)

                # 5. Spawns & Triggers
                elif spec_type == 'PLAYER_SPAWN':
                    player_spawn = (x, y)

                elif spec_type in ['NPC_ZE', 'NPC_JEGUE']:
                    npc_ze = NPC(
                        x=x, y=y - 24, name="Jegue do Sertão", label="JEGUE",
                        dialogue_pages=[
                            "Ôente, Lampião! A Catita foi levada pro outro lado da caatinga!",
                            "Cuidado com os cangaceiros, cactos e as tanajuras pelo caminho!",
                            "Use [W,A,S,D] para mover e pular, [SHIFT] para dar um pique e [F] para atirar!",
                            "Segure para CIMA [W] ou para BAIXO [S] para direcionar seus tiros.",
                            "Siga em frente no sertão e traga a Catita de volta!"
                        ]
                    )
                    npcs.append(npc_ze)

                elif spec_type == 'NPC_BEMZEDOR':
                    npc_bemzedor = NPC(
                        x=x, y=y - 24, name="Bemzedor", label="BENZEDOR",
                        sprite_path="assets/sprites/bemzedor/bemzedor-idle.png",
                        dialogue_pages=[
                            "Que a benção do sertão lhe acompanhe, meu filho!",
                            "Vou lhe benzer para restaurar suas forças e curar suas feridas."
                        ]
                    )
                    npcs.append(npc_bemzedor)

                elif spec_type == 'ENEMY':
                    patrol_dist = spec.get('patrol_dist', 150)
                    enemy = ChaserEnemy(x=x, y=y, patrol_dist=patrol_dist)
                    enemies.append(enemy)

                elif spec_type == 'ENEMY_TANAJURA':
                    patrol_dist = spec.get('patrol_dist', 120)
                    enemy = TanajuraEnemy(x=x, y=y, patrol_dist=patrol_dist)
                    enemies.append(enemy)

                elif spec_type == 'VACA_MOJADA':
                    vaca_mojada = VacaMojada(x=x, y=y - 32, trigger_x=x - 100)

                elif spec_type == 'FINISH_TRIGGER':
                    finish_trigger = pygame.Rect(x, y, 100, 160)

        return {
            'solid_tiles': solid_tiles,
            'hazards': hazards,
            'collectibles': collectibles,
            'props': props,
            'npcs': npcs,
            'enemies': enemies,
            'vaca_mojada': vaca_mojada,
            'player_spawn': player_spawn,
            'finish_trigger': finish_trigger,
            'level_width': level_width,
            'level_height': level_height
        }
