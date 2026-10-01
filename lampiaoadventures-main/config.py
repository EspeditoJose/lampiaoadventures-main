"""
Configuration module for Lampião Adventures.
Contains screen settings, physics parameters, color palettes, and input keys.
"""

import pygame

# Screen & Display Settings
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60
TITLE = "Lampião Adventures: The Busca of The Catita"

# Zoom / Render Scale factor (Player occupies ~1/6th of screen height)
RENDER_SCALE = 2.4
VIRTUAL_WIDTH = int(SCREEN_WIDTH / RENDER_SCALE)    # 533 px
VIRTUAL_HEIGHT = int(SCREEN_HEIGHT / RENDER_SCALE)  # 300 px

# Colors (Sertão / Backlands Palette)
COLOR_BACKGROUND = (245, 222, 179)     # Sertão Warm Sand / Wheat
COLOR_SKY = (255, 218, 185)            # Peach Sunset Sky
COLOR_SUN = (255, 140, 0)              # Deep Sun Orange
COLOR_GROUND = (180, 100, 45)          # Terracotta Earth
COLOR_TILE = (160, 82, 45)            # Saddle Brown Clay
COLOR_TILE_BORDER = (100, 45, 20)      # Dark Terracotta Border
COLOR_HAZARD = (220, 20, 60)           # Crimson Cactus Spikes
COLOR_COLLECTIBLE = (255, 215, 0)      # Gold Catita Coin

# Entity Colors (Fallback Placeholders)
COLOR_PLAYER = (204, 119, 34)          # Cangaço Leather Brown
COLOR_PLAYER_OUTLINE = (102, 51, 0)
COLOR_ENEMY_PATROL = (178, 34, 34)     # Firebrick Red
COLOR_ENEMY_CHASE = (255, 69, 0)       # Burning Orange Red
COLOR_NPC = (46, 139, 87)              # Sea Green (Severino / Zé)
COLOR_PROP = (139, 69, 19)             # Saddle Brown Wood

# UI Colors
COLOR_WHITE = (255, 255, 255)
COLOR_BLACK = (0, 0, 0)
COLOR_GRAY = (128, 128, 128)
COLOR_DARK_GRAY = (40, 40, 40)
COLOR_HEALTH_GREEN = (50, 205, 50)
COLOR_HEALTH_RED = (220, 20, 60)
COLOR_STAMINA_BLUE = (30, 144, 255)
COLOR_STAMINA_YELLOW = (255, 191, 0)
COLOR_DIALOGUE_BG = (20, 20, 25, 235)
COLOR_DIALOGUE_BORDER = (212, 175, 55) # Gold Border

# Physics & Player Constants
GRAVITY = 0.8
MAX_FALL_SPEED = 15.0
PLAYER_SPEED = 4.5
PLAYER_SPRINT_SPEED = 7.5
PLAYER_JUMP_FORCE = -14.5
MAX_HEALTH = 100
MAX_STAMINA = 100.0
STAMINA_DRAIN = 0.75
STAMINA_RECHARGE = 0.4
STAMINA_RECHARGE_DELAY = 30

# Level Dimensions (7680x720 horizontal map)
LEVEL_WIDTH = 7680
LEVEL_HEIGHT = 720
TILE_SIZE = 40

# Key Bindings
KEY_LEFT = [pygame.K_a, pygame.K_LEFT]
KEY_RIGHT = [pygame.K_d, pygame.K_RIGHT]
KEY_UP = [pygame.K_w, pygame.K_UP]
KEY_DOWN = [pygame.K_s, pygame.K_DOWN]
KEY_JUMP = [pygame.K_w, pygame.K_SPACE, pygame.K_UP]
KEY_SPRINT = [pygame.K_LSHIFT, pygame.K_RSHIFT]
KEY_INTERACT = [pygame.K_e]
KEY_SHOOT = [pygame.K_j, pygame.K_f, pygame.K_k, pygame.K_LCTRL]
KEY_PAUSE = [pygame.K_ESCAPE, pygame.K_p]
KEY_CONFIRM = [pygame.K_RETURN, pygame.K_SPACE, pygame.K_e]
