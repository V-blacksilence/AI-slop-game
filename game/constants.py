# Game Constants
import pygame

# Window settings
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (220, 53, 69)
GREEN = (40, 167, 69)
BLUE = (0, 123, 255)
YELLOW = (255, 193, 7)
ORANGE = (253, 126, 20)
PURPLE = (111, 66, 193)
GRAY = (108, 117, 125)
DARK_GRAY = (52, 58, 64)
LIGHT_GRAY = (173, 181, 189)

# Player settings
PLAYER_SPEED = 5
PLAYER_MAX_HEALTH = 100
PLAYER_MAX_STAMINA = 100
PLAYER_STAMINA_REGEN = 1
PLAYER_SIZE = 40
PLAYER_DAMAGE = 20

# Combat settings
DODGE_COST = 25
BLOCK_COST_PER_FRAME = 0.8
DODGE_DURATION = 15  # frames
DODGE_DISTANCE = 150
BLOCK_DAMAGE_REDUCTION = 0.7
PERFECT_DODGE_WINDOW = 8  # frames before hit
PERFECT_BLOCK_WINDOW = 5  # frames of block start
ATTACK_COOLDOWN = 30  # frames
ATTACK_RANGE = 100

# Enemy settings
ENEMY_TYPES = {
    'grunt': {
        'health': 50,
        'damage': 10,
        'speed': 2,
        'color': RED,
        'size': 35,
        'xp': 10
    },
    'brute': {
        'health': 100,
        'damage': 20,
        'speed': 1.5,
        'color': ORANGE,
        'size': 45,
        'xp': 25
    },
    'assassin': {
        'health': 40,
        'damage': 15,
        'speed': 4,
        'color': PURPLE,
        'size': 30,
        'xp': 20
    }
}

BOSS_MULTIPLIER = 3  # Boss stats multiplier

# Level settings
LEVEL_SIZE = 2000
ROOM_MIN_SIZE = 400
ROOM_MAX_SIZE = 800
ENEMIES_PER_LEVEL = 8
BOSS_LEVEL_INTERVAL = 3

# Item drop rates
DROP_RATES = {
    'health_potion': 0.3,
    'weapon_upgrade': 0.15,
    'armor_upgrade': 0.1
}

# Meta progression
META_CURRENCY_NAME = 'souls'
META_UPGRADES = {
    'max_health': {'cost': 10, 'increment': 10},
    'max_stamina': {'cost': 8, 'increment': 10},
    'damage': {'cost': 15, 'increment': 5},
    'speed': {'cost': 12, 'increment': 0.5}
}

LEVEL_HEAL_AMOUNT = 20
PARTICLE_COUNT = 10
ITEM_COLLECTION_RANGE = 50
ATTACK_CONE_ANGLE = 0.5  
PRATICLE_LIFETIME = 30  